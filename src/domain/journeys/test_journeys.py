from datetime import date, datetime, timedelta
from typing import List

from src.domain.journeys.service import JourneySearchService


class EventStub:
    """Stub mínimo para simular FlightEventDTO."""

    def __init__(
        self,
        flight_number: str,
        from_city: str,
        to_city: str,
        departure_time: str,
        arrival_time: str,
    ):
        self.flight_number = flight_number
        self.from_city = from_city
        self.to_city = to_city
        self.departure_time = datetime.fromisoformat(departure_time)
        self.arrival_time = datetime.fromisoformat(arrival_time)


class StubFlightEventService:
    """Implementación fake de FlightEventService para tests."""

    def __init__(self, events: List[EventStub]):
        self._events = events

    def list_all(self) -> List[EventStub]:
        return self._events


def build_default_events() -> List[EventStub]:
    """Dataset con todos los escenarios que queremos testear."""
    return [
        # --- EZE - MIA, directos y conexiones (02-01) ---
        EventStub("AR1000", "EZE", "MIA",
                  "2025-02-01T08:00:00", "2025-02-01T16:00:00"),
        EventStub("AR2000", "EZE", "MAD",
                  "2025-02-01T09:00:00", "2025-02-01T21:00:00"),
        EventStub("IB2001", "MAD", "MIA",
                  "2025-02-01T22:00:00", "2025-02-02T05:00:00"),
        EventStub("LA3000", "EZE", "GRU",
                  "2025-02-01T07:00:00", "2025-02-01T10:00:00"),
        # conexión válida vía GRU
        EventStub("AA3001", "GRU", "MIA",
                  "2025-02-01T12:00:00", "2025-02-01T18:30:00"),
        # conexión inválida vía GRU (espera > 4hs)
        EventStub("AA9999", "GRU", "MIA",
                  "2025-02-01T16:00:00", "2025-02-01T22:00:00"),

        # --- EZE - MIA directo en otra fecha (02-02) ---
        EventStub("AR1001", "EZE", "MIA",
                  "2025-02-02T09:00:00", "2025-02-02T17:00:00"),

        # --- HKG - NRT: directo + conexión válida + conexión inválida (espera > 4hs) ---
        EventStub("HK100", "HKG", "NRT", "2025-03-05T07:30:00",
                  "2025-03-05T12:30:00"),
        EventStub("HK200", "HKG", "MNL", "2025-03-05T08:00:00",
                  "2025-03-05T10:00:00"),
        EventStub("PR201", "MNL", "NRT", "2025-03-05T12:00:00",
                  "2025-03-05T17:00:00"),
        EventStub("PR202", "MNL", "NRT", "2025-03-05T15:00:00",
                  "2025-03-05T20:00:00"),

        # --- FRA - LHR: solo conexiones (y una inválida por horario) ---
        EventStub("LH100", "FRA", "CDG", "2025-04-10T08:00:00",
                  "2025-04-10T09:30:00"),
        # válido: sale después de llegar a CDG
        EventStub("AF101", "CDG", "LHR", "2025-04-10T11:00:00",
                  "2025-04-10T12:00:00"),
        # inválido: sale antes de que llegue el vuelo de FRA
        EventStub("AF102", "CDG", "LHR", "2025-04-10T09:15:00",
                  "2025-04-10T10:15:00"),

        # --- EZE - SCL - MIA: conexión con espera > 4hs (debe descartarse) ---
        EventStub("AR1500", "EZE", "SCL",
                  "2025-01-20T07:00:00", "2025-01-20T10:00:00"),
        EventStub("LA1501", "SCL", "MIA",
                  "2025-01-20T15:30:00", "2025-01-20T23:30:00"),

        # --- LHR - JFK ida/vuelta para no interferir pero testear otros casos potenciales ---
        EventStub("BA600", "LHR", "JFK", "2025-02-10T12:00:00",
                  "2025-02-10T15:00:00"),
        EventStub("BA601", "JFK", "LHR", "2025-02-10T17:00:00",
                  "2025-02-11T05:00:00"),
    ]


# ---------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------

def test_eze_mia_direct_and_connections():
    """Debe encontrar: vuelo directo + 2 conexiones válidas, y ordenar por conexiones y duración."""
    events = build_default_events()
    service = JourneySearchService(StubFlightEventService(events))

    journeys = service.search(date(2025, 2, 1), "EZE", "MIA")

    # directo + 2 con escala
    assert len(journeys) == 3

    # 1) primer resultado debe ser el vuelo directo
    direct = journeys[0]
    assert direct.connections == 1
    assert len(direct.path) == 1
    assert direct.path[0].flight_number == "AR1000"

    # 2) verificar que existan las dos conexiones válidas
    routes = [[seg.flight_number for seg in j.path] for j in journeys]

    assert ["LA3000", "AA3001"] in routes  # vía GRU
    assert ["AR2000", "IB2001"] in routes  # vía MAD

    # 3) la conexión con espera > 4h NO debe aparecer
    assert ["LA3000", "AA9999"] not in routes

    # 4) las conexiones deben estar ordenadas por duración total (GRU más corta que MAD)
    #    O sea, LA3000+AA3001 debe ir antes que AR2000+IB2001
    connections_only = [j for j in journeys if j.connections == 2]
    assert len(connections_only) == 2

    durations = [
        (j.path[0].flight_number, j.path[-1].flight_number,
         j.path[-1].arrival_time - j.path[0].departure_time)
        for j in connections_only
    ]

    # dict para mirar por código
    duration_by_route = {
        (a, b): d for (a, b, d) in durations
    }

    assert duration_by_route[("LA3000", "AA3001")
                             ] < duration_by_route[("AR2000", "IB2001")]


def test_eze_mia_direct_only_other_date():
    """Para otra fecha, solo debe devolver el vuelo directo disponible."""
    events = build_default_events()
    service = JourneySearchService(StubFlightEventService(events))

    journeys = service.search(date(2025, 2, 2), "EZE", "MIA")

    assert len(journeys) == 1
    j = journeys[0]
    assert j.connections == 1
    assert len(j.path) == 1
    assert j.path[0].flight_number == "AR1001"


def test_hkg_nrt_direct_and_connection():
    """HKG -> NRT: directo + una conexión válida; la otra conexión con espera > 4h se descarta."""
    events = build_default_events()
    service = JourneySearchService(StubFlightEventService(events))

    journeys = service.search(date(2025, 3, 5), "HKG", "NRT")

    # directo + 1 conexión válida
    assert len(journeys) == 2

    routes = [[seg.flight_number for seg in j.path] for j in journeys]

    assert ["HK100"] in routes  # directo
    assert ["HK200", "PR201"] in routes  # conexión válida
    assert ["HK200", "PR202"] not in routes  # conexión inválida (espera > 4h)

    # directo primero
    assert journeys[0].path[0].flight_number == "HK100"


def test_fra_lhr_only_valid_connection():
    """FRA -> LHR: debe usar sólo la conexión LH100 + AF101, ya que AF102 sale antes de que llegue el vuelo."""
    events = build_default_events()
    service = JourneySearchService(StubFlightEventService(events))

    journeys = service.search(date(2025, 4, 10), "FRA", "LHR")

    assert len(journeys) == 1
    j = journeys[0]
    assert j.connections == 2
    route = [seg.flight_number for seg in j.path]
    assert route == ["LH100", "AF101"]


def test_eze_mia_long_connection_wait_is_discarded():
    """EZE -> MIA el 20/01: la única ruta tiene espera > 4h, por lo que no debería haber journeys."""
    events = build_default_events()
    service = JourneySearchService(StubFlightEventService(events))

    journeys = service.search(date(2025, 1, 20), "EZE", "MIA")

    assert journeys == []


def test_total_duration_over_24h_is_discarded():
    """Caso artificial donde la duración total del viaje supera las 24 horas."""
    events = [
        # primer tramo: 00:00 -> 01:00
        EventStub("LONG1", "AAA", "BBB", "2025-05-01T00:00:00",
                  "2025-05-01T01:00:00"),
        # segundo tramo: 23:30 -> siguiente día 23:30 (casi +47.5h total)
        EventStub("LONG2", "BBB", "CCC", "2025-05-01T23:30:00",
                  "2025-05-02T23:30:00"),
    ]
    service = JourneySearchService(StubFlightEventService(events))

    journeys = service.search(date(2025, 5, 1), "AAA", "CCC")

    # por la regla total_duration > 24h se debe descartar
    assert journeys == []


def test_no_results_when_no_route():
    """Si no hay vuelos que conecten origen y destino, debe devolver lista vacía."""
    events = build_default_events()
    service = JourneySearchService(StubFlightEventService(events))

    journeys = service.search(date(2025, 2, 1), "FRA", "MIA")

    assert journeys == []

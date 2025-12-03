from datetime import date, datetime, timedelta
from typing import Dict, List
import logging

from src.domain.flight_events.service import FlightEventService, FlightEventDTO

logger = logging.getLogger(__name__)


class JourneySegmentDTO:
    def __init__(
        self,
        flight_number: str,
        from_city: str,
        to_city: str,
        departure_time: datetime,
        arrival_time: datetime,
    ):
        self.flight_number = flight_number
        self.from_city = from_city
        self.to_city = to_city
        self.departure_time = departure_time
        self.arrival_time = arrival_time


class JourneyDTO:
    def __init__(self, connections: int, path: List[JourneySegmentDTO]):
        self.connections = connections
        self.path = path


class JourneySearchService:
    def __init__(self, flight_event_service: FlightEventService):
        self._flight_event_service = flight_event_service

    def search(self, flight_date: date, from_city: str, to_city: str) -> List[JourneyDTO]:
        max_total_duration = timedelta(hours=24)
        max_connection_wait = timedelta(hours=4)
        journeys: List[JourneyDTO] = []
        all_events: List[FlightEventDTO] = self._flight_event_service.list_all()
        flights = [e for e in all_events if e.departure_time.date()
                   == flight_date]

        flights_by_origin: Dict[str, List[FlightEventDTO]] = {}
        for f in flights:
            flights_by_origin.setdefault(f.from_city, []).append(f)

        first_part = flights_by_origin.get(from_city, [])

        for f1 in first_part:
            # Caso 1: Vuelo directo
            if f1.to_city == to_city:
                journeys.append(
                    JourneyDTO(
                        connections=1,
                        path=[
                            JourneySegmentDTO(
                                flight_number=f1.flight_number,
                                from_city=f1.from_city,
                                to_city=f1.to_city,
                                departure_time=f1.departure_time,
                                arrival_time=f1.arrival_time,
                            )
                        ],
                    )
                )

            # Caso 2: Vuelos con escala
            second_part = flights_by_origin.get(f1.to_city, [])

            for f2 in second_part:
                # No va a donde quiero llegar
                if f2.to_city != to_city:
                    continue

                # Ya salio cuando yo llegue a la escala
                if f2.departure_time <= f1.arrival_time:
                    continue

                # Hay que esperar mas de 4hs entre vuelos
                connection_wait = f2.departure_time - f1.arrival_time
                if connection_wait > max_connection_wait:
                    continue

                # La duracion total del viaje es mayor a 24hs
                total_duration = f2.arrival_time - f1.departure_time
                if total_duration > max_total_duration:
                    continue

                journeys.append(
                    JourneyDTO(
                        connections=2,
                        path=[
                            JourneySegmentDTO(
                                flight_number=f1.flight_number,
                                from_city=f1.from_city,
                                to_city=f1.to_city,
                                departure_time=f1.departure_time,
                                arrival_time=f1.arrival_time,
                            ),
                            JourneySegmentDTO(
                                flight_number=f2.flight_number,
                                from_city=f2.from_city,
                                to_city=f2.to_city,
                                departure_time=f2.departure_time,
                                arrival_time=f2.arrival_time,
                            ),
                        ],
                    )
                )

        # Ordenamos primero por cantidad de conexiones y segundo por duracion total del viaje
        journeys.sort(
            key=lambda j: (
                j.connections,
                j.path[-1].arrival_time - j.path[0].departure_time,
            )
        )

        return journeys

from pathlib import Path
from dependency_injector import containers, providers
from .service import FlightEventService


class FlightEventsModule(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=[".controller"])

    root = providers.DependenciesContainer()

    data_path = str(Path(__file__).parent / "flight_events.json")

    service = providers.Factory(
        FlightEventService,
        data_path=data_path
    )

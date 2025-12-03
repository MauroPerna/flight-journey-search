from dependency_injector import containers, providers
from .service import JourneySearchService
from src.domain.flight_events.service import FlightEventService


class JourneysModule(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=[".controller"])

    root = providers.DependenciesContainer()

    service = providers.Factory(
        JourneySearchService,
        flight_event_service=root.flight_event_service,
    )

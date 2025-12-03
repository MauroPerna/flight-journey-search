from fastapi import FastAPI
from dependency_injector import providers


def register_modules(app: FastAPI):
    # =========================
    # FlightEvents
    # =========================
    from src.domain.flight_events.module import FlightEventsModule
    from src.domain.flight_events.controller import router as flight_router

    flight_events_container = FlightEventsModule(
        root=providers.DependenciesContainer()
    )
    flight_events_container.wire(
        modules=["src.domain.flight_events.controller"])
    app.include_router(flight_router)
    app.state.flight_events_container = flight_events_container

    # =========================
    # Journeys
    # =========================
    from src.domain.journeys.module import JourneysModule
    from src.domain.journeys.controller import router as journeys_router

    journeys_container = JourneysModule(
        root=providers.DependenciesContainer(
            flight_event_service=flight_events_container.service
        )
    )

    journeys_container.wire(modules=["src.domain.journeys.controller"])
    app.include_router(journeys_router)
    app.state.journeys_container = journeys_container

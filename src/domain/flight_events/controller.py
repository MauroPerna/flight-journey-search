from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel

from .service import FlightEventService
from .module import FlightEventsModule

router = APIRouter(prefix="/flight-events", tags=["flight-events"])


class FlightEvent(BaseModel):
    flight_number: str
    from_city: str
    to_city: str
    departure_time: datetime
    arrival_time: datetime


@router.get("", response_model=List[FlightEvent])
@inject
async def list_flight_events(
    service: FlightEventService = Depends(Provide[FlightEventsModule.service]),
) -> List[FlightEvent]:
    dtos = service.list_all()
    return [
        FlightEvent(
            flight_number=d.flight_number,
            from_city=d.from_city,
            to_city=d.to_city,
            departure_time=d.departure_time,
            arrival_time=d.arrival_time,
        )
        for d in dtos
    ]

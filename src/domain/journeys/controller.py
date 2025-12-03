from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel

from .service import JourneySearchService, JourneyDTO
from .module import JourneysModule

router = APIRouter(prefix="/journeys", tags=["journeys"])


class JourneySegment(BaseModel):
    flight_number: str
    from_city: str
    to_city: str
    departure_time: datetime
    arrival_time: datetime


class Journey(BaseModel):
    connections: int
    path: List[JourneySegment]


class JourneySearchRequest(BaseModel):
    date: datetime
    from_city: str
    to_city: str


@router.get("/search", response_model=List[Journey])
@inject
async def search_journeys(
    date: datetime,
    from_city: str,
    to_city: str,
    service: JourneySearchService = Depends(Provide[JourneysModule.service]),
) -> List[Journey]:
    dtos: List[JourneyDTO] = service.search(
        flight_date=date.date(),
        from_city=from_city,
        to_city=to_city,
    )

    return [
        Journey(
            connections=j.connections,
            path=[
                JourneySegment(
                    flight_number=s.flight_number,
                    from_city=s.from_city,
                    to_city=s.to_city,
                    departure_time=s.departure_time,
                    arrival_time=s.arrival_time,
                )
                for s in j.path
            ],
        )
        for j in dtos
    ]

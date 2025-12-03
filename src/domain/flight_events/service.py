import json
from pathlib import Path
from typing import List
from datetime import datetime


class FlightEventDTO:
    def __init__(self, event_id: str, flight_number: str, from_city: str, to_city: str,
                 departure_time: datetime, arrival_time: datetime):
        self.event_id = event_id
        self.flight_number = flight_number
        self.from_city = from_city
        self.to_city = to_city
        self.departure_time = departure_time
        self.arrival_time = arrival_time


class FlightEventService:
    def __init__(self, data_path: str):
        self.data_path = data_path

    def list_all(self) -> List[FlightEventDTO]:
        file_path = Path(self.data_path)

        with file_path.open("r") as f:
            events = json.load(f)

        result = []

        for e in events:
            result.append(FlightEventDTO(
                event_id=e["event_id"],
                flight_number=e["flight_number"],
                from_city=e["from"],
                to_city=e["to"],
                departure_time=datetime.fromisoformat(e["departure_time"]),
                arrival_time=datetime.fromisoformat(e["arrival_time"]),
            ))

        return result

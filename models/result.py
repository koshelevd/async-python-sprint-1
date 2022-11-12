from pydantic import BaseModel


class Stat(BaseModel):
    date: str
    no_rain_hours: int
    avg_temp_per_day: float


class Result(BaseModel):
    city: str
    stats: list[Stat]
    avg_temp_all_days: float
    avg_no_rain_hours: float

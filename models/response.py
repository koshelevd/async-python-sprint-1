from pydantic import BaseModel, Field


class Tzinfo(BaseModel):
    name: str
    abbr: str
    dst: bool
    offset: int


class Info(BaseModel):
    n: bool
    geoid: int
    url: str
    lat: float
    lon: float
    tzinfo: Tzinfo
    def_pressure_mm: int
    def_pressure_pa: int
    slug: str
    zoom: int
    nr: bool
    ns: bool
    nsr: bool
    p: bool
    f: bool
    _h: bool


class District(BaseModel):
    id: int
    name: str


class Locality(BaseModel):
    id: int
    name: str


class Province(BaseModel):
    id: int
    name: str


class Country(BaseModel):
    id: int
    name: str


class GeoObject(BaseModel):
    district: District | None
    locality: Locality
    province: Province
    country: Country


class Yesterday(BaseModel):
    temp: int


class AccumPrec(BaseModel):
    field_1: float = Field(..., alias='1')
    field_7: float = Field(..., alias='7')
    field_3: float = Field(..., alias='3')


class Fact(BaseModel):
    obs_time: int
    uptime: int
    temp: int
    feels_like: int
    icon: str
    condition: str
    cloudness: float
    prec_type: int
    prec_prob: int
    prec_strength: int
    is_thunder: bool
    wind_speed: float
    wind_dir: str
    pressure_mm: int
    pressure_pa: int
    humidity: int
    daytime: str
    polar: bool
    season: str
    source: str
    accum_prec: AccumPrec | None
    soil_moisture: float | None
    soil_temp: int | None
    uv_index: int
    wind_gust: float


class Hour(BaseModel):
    hour: str
    hour_ts: int
    temp: int
    feels_like: int
    icon: str
    condition: str
    cloudness: float
    prec_type: int
    prec_strength: float
    is_thunder: bool
    wind_dir: str
    wind_speed: float
    wind_gust: float
    pressure_mm: int
    pressure_pa: int
    humidity: int
    uv_index: int
    soil_temp: int | None
    soil_moisture: float | None
    prec_mm: float
    prec_period: int
    prec_prob: int


class Biomet(BaseModel):
    index: int
    condition: str


class Forecast(BaseModel):
    date: str
    date_ts: int
    week: int
    sunrise: str
    sunset: str
    rise_begin: str
    set_end: str
    moon_code: int
    moon_text: str
    hours: list[Hour]
    biomet: Biomet | None = None


class YandexResponse(BaseModel):
    now: int
    now_dt: str
    info: Info
    geo_object: GeoObject
    yesterday: Yesterday
    fact: Fact
    forecasts: list[Forecast]

from pydantic import BaseModel


class Tender(BaseModel):
    ref_id: str
    name: str
    url: str
    startAt: str
    endAt: str
    budget: int | None

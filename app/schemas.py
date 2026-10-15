from pydantic import BaseModel, ConfigDict


class PriceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticker: str
    price: float
    timestamp: int

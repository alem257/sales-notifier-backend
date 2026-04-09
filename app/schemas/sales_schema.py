from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SaleCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=100)
    product_name: str = Field(min_length=1, max_length=100)
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    currency: str = Field(default="USD", min_length=1, max_length=10)
    status: str = Field(default="completed", min_length=1, max_length=20)
    sync_to_google_sheets: bool = False


class SaleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    product_name: str
    amount: Decimal
    currency: str
    status: str
    sync_to_google_sheets: bool
    created_at: datetime

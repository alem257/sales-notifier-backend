from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.sales_schema import SaleCreate, SaleRead
from app.services import sales_service

router = APIRouter(prefix="/sales", tags=["sales"])


@router.get("", response_model=list[SaleRead])
def list_sales(db: Session = Depends(get_db)) -> list[SaleRead]:
    """Lista todas las ventas, de la más reciente a la más antigua."""
    return sales_service.list_sales(db)


@router.get("/{sale_id}", response_model=SaleRead)
def get_sale(sale_id: int, db: Session = Depends(get_db)) -> SaleRead:
    """Obtiene una venta por su id."""
    sale = sales_service.get_sale(db, sale_id)
    if sale is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada")
    return SaleRead.model_validate(sale)


@router.post("", response_model=SaleRead, status_code=status.HTTP_201_CREATED)
def register_sale(payload: SaleCreate, db: Session = Depends(get_db)) -> SaleRead:
    """Crea una venta y notifica a n8n."""
    return sales_service.create_sale(db, payload)

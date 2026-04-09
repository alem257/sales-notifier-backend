from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Sale
from app.schemas.sales_schema import SaleCreate, SaleRead
from app.utils.notifier import notify_n8n


def _sale_to_webhook_payload(sale: Sale) -> dict:
    return {
        "event": "sale_created",
        "sale_id": sale.id,
        "customer_name": sale.customer_name,
        "product_name": sale.product_name,
        "amount": str(sale.amount),
        "currency": sale.currency,
        "status": sale.status,
        "sync_to_google_sheets": sale.sync_to_google_sheets,
        "created_at": sale.created_at.isoformat() if sale.created_at else None,
    }


def create_sale(db: Session, data: SaleCreate) -> SaleRead:
    sale = Sale(
        customer_name=data.customer_name,
        product_name=data.product_name,
        amount=data.amount,
        currency=data.currency,
        status=data.status,
        sync_to_google_sheets=data.sync_to_google_sheets,
    )
    db.add(sale)
    db.commit()
    db.refresh(sale)

    notify_n8n(_sale_to_webhook_payload(sale))

    return SaleRead.model_validate(sale)


def list_sales(db: Session) -> list[SaleRead]:
    stmt = select(Sale).order_by(Sale.created_at.desc())
    rows = db.scalars(stmt).all()
    return [SaleRead.model_validate(s) for s in rows]


def get_sale(db: Session, sale_id: int) -> Sale | None:
    return db.get(Sale, sale_id)

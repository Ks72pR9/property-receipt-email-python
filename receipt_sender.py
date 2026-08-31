"""Business workflow for a property-management backend."""
from dataclasses import dataclass
from datetime import date
from html import escape
from typing import Any, Protocol


@dataclass(frozen=True)
class TenantDocument:
    name: str
    received_on: date


@dataclass(frozen=True)
class MaintenanceRequest:
    title: str
    open: bool


@dataclass(frozen=True)
class InspectionReminder:
    due_on: date


@dataclass(frozen=True)
class PropertyOrder:
    order_id: str
    tenant_name: str
    tenant_email: str
    amount_cents: int
    paid: bool
    documents: tuple[TenantDocument, ...] = ()
    maintenance: tuple[MaintenanceRequest, ...] = ()
    inspection: InspectionReminder | None = None


class EmailSender(Protocol):
    class Email(Protocol):
        def send(self, *, to: str, subject: str, html: str) -> dict[str, Any]: ...

    email: Email


def receipt_html(order: PropertyOrder) -> str:
    open_items = sum(item.open for item in order.maintenance)
    inspection = order.inspection.due_on.isoformat() if order.inspection else "not scheduled"
    return (f"<h1>Receipt {escape(order.order_id)}</h1>"
            f"<p>Tenant: {escape(order.tenant_name)}</p>"
            f"<p>Paid: ${order.amount_cents / 100:.2f}</p>"
            f"<p>Documents: {len(order.documents)} | Open maintenance: {open_items}</p>"
            f"<p>Next inspection: {escape(inspection)}</p>")


def send_receipt(order: PropertyOrder, sender: EmailSender) -> str | None:
    """Return the message id only when payment is settled."""
    if not order.paid:
        return None
    result = sender.email.send(to=order.tenant_email, subject=f"Receipt for order {order.order_id}", html=receipt_html(order))
    return str(result["message_id"])

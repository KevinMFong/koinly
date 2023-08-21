from datetime import datetime
from typing import Any
from typing import NamedTuple
from typing import Optional

from marshmallow import Schema
from marshmallow import fields
from marshmallow import post_load

__all__ = (
    "ReportTransaction",
    "ReportTransactionSchema",
)


class ReportTransaction(NamedTuple):
    date: datetime
    net_value_usd: float
    type: str  # TODO convert to enum
    description: Optional[str] = None
    fee_amount: Optional[float] = None
    fee_currency: Optional[str] = None
    fee_value_usd: Optional[float] = None
    gain_usd: Optional[float] = None
    id: Optional[str] = None
    label: Optional[str] = None  # TODO convert to enum
    received_amount: Optional[float] = None
    received_cost_basis: Optional[float] = None
    received_currency: Optional[str] = None
    receiving_wallet: Optional[str] = None
    sending_wallet: Optional[str] = None
    sent_amount: Optional[float] = None
    sent_cost_basis: Optional[float] = None
    sent_currency: Optional[str] = None
    tx_dest: Optional[str] = None
    tx_hash: Optional[str] = None
    tx_src: Optional[str] = None


class ReportTransactionSchema(Schema):
    class Meta:
        ordered = True

    id = fields.String(required=False)
    date = fields.DateTime(required=True)
    type = fields.String(required=True)
    label = fields.String(required=False, missing=None)
    sending_wallet = fields.String(required=False, missing=None)
    sent_amount = fields.Float(required=False, missing=None)
    sent_currency = fields.String(required=False, missing=None)
    sent_cost_basis = fields.Float(required=False, missing=None)
    receiving_wallet = fields.String(required=False, missing=None)
    received_amount = fields.Float(required=False, missing=None)
    received_currency = fields.String(required=False, missing=None)
    received_cost_basis = fields.Float(required=False, missing=None)
    fee_amount = fields.Float(required=False, missing=None)
    fee_currency = fields.String(required=False, missing=None)
    gain_usd = fields.Float(required=False, missing=None)
    net_value_usd = fields.Float(required=True)
    fee_value_usd = fields.Float(required=False, missing=None)
    tx_src = fields.String(required=False, missing=None)
    tx_dest = fields.String(required=False, missing=None)
    tx_hash = fields.String(required=False, missing=None)
    description = fields.String(required=False, missing=None)

    @post_load
    def deserialize(self, data: dict, **kwargs: Any) -> Any:
        return ReportTransaction(**data)

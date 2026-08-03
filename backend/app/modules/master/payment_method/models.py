from app.core.extensions import db
from app.core.base_model import BaseModel

class PaymentMethod(db.Model, BaseModel):
    __tablename__ = "payment_methods"
    code          = db.Column(db.String(20),  nullable=False)
    name          = db.Column(db.String(100), nullable=False)
    description   = db.Column(db.Text, nullable=True)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    __table_args__ = (
        db.UniqueConstraint("code", name="uq_payment_methods_code"),
        db.Index("ix_payment_methods_code", "code"),
    )

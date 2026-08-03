from app.core.extensions import db
from app.core.base_model import BaseModel

class CancellationPolicy(db.Model, BaseModel):
    __tablename__ = "cancellation_policies"
    code               = db.Column(db.String(20),  nullable=False)
    name               = db.Column(db.String(100), nullable=False)
    description        = db.Column(db.Text, nullable=True)
    display_order      = db.Column(db.Integer, default=0, nullable=False)
    refund_percentage  = db.Column(db.Numeric(5, 2), nullable=False)
    days_before_travel = db.Column(db.Integer, nullable=False)
    policy_type        = db.Column(db.String(20), nullable=False, default='PERCENTAGE')
    __table_args__ = (
        db.UniqueConstraint("code", name="uq_cancellation_policies_code"),
        db.Index("ix_cancellation_policies_code", "code"),
    )

from app.core.extensions import db
from app.core.base_model import BaseModel

class TaxConfiguration(db.Model, BaseModel):
    __tablename__ = "tax_configurations"
    code          = db.Column(db.String(20),  nullable=False)
    name          = db.Column(db.String(100), nullable=False)
    description   = db.Column(db.Text, nullable=True)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    tax_rate      = db.Column(db.Numeric(5, 2), nullable=False)
    tax_type      = db.Column(db.String(20), nullable=False)
    is_inclusive  = db.Column(db.Boolean, default=False, nullable=False)
    is_default    = db.Column(db.Boolean, default=False, nullable=False, index=True)
    __table_args__ = (
        db.UniqueConstraint("code", name="uq_tax_configurations_code"),
        db.Index("ix_tax_configurations_code", "code"),
    )

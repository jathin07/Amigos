from app.core.extensions import db
from app.core.base_model import BaseModel

class Currency(db.Model, BaseModel):
    __tablename__ = "currencies"
    code          = db.Column(db.String(20),  nullable=False)
    name          = db.Column(db.String(100), nullable=False)
    description   = db.Column(db.Text, nullable=True)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    symbol        = db.Column(db.String(5), nullable=False)
    is_default    = db.Column(db.Boolean, default=False, nullable=False, index=True)
    __table_args__ = (
        db.UniqueConstraint("code", name="uq_currencies_code"),
        db.Index("ix_currencies_code", "code"),
    )

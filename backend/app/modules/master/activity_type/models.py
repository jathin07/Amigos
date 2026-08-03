from app.core.extensions import db
from app.core.base_model import BaseModel

class ActivityType(db.Model, BaseModel):
    __tablename__ = "activity_types"
    code          = db.Column(db.String(20),  nullable=False)
    name          = db.Column(db.String(100), nullable=False)
    description   = db.Column(db.Text, nullable=True)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    __table_args__ = (
        db.UniqueConstraint("code", name="uq_activity_types_code"),
        db.Index("ix_activity_types_code", "code"),
    )

from app.core.extensions import db
from app.core.base_model import BaseModel

class MealPlan(db.Model, BaseModel):
    __tablename__ = "meal_plans"
    code          = db.Column(db.String(20),  nullable=False)
    name          = db.Column(db.String(100), nullable=False)
    description   = db.Column(db.Text, nullable=True)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    __table_args__ = (
        db.UniqueConstraint("code", name="uq_meal_plans_code"),
        db.Index("ix_meal_plans_code", "code"),
    )

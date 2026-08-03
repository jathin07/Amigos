import uuid
from app.core.extensions import db
from app.core.base_model import BaseModel

class City(db.Model, BaseModel):
    __tablename__ = "cities"

    district_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("districts.id", ondelete="RESTRICT"), nullable=False)  
    state_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("states.id", ondelete="RESTRICT"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0)

    state = db.relationship("State", backref="cities")
    district = db.relationship("District", backref="cities")

    __table_args__ = (
        db.UniqueConstraint('code', 'state_id', name='uq_city_code_state'),
        db.Index('ix_cities_state_id', 'state_id'),
    )

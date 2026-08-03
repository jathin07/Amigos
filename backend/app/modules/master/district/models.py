import uuid
from app.core.extensions import db
from app.core.base_model import BaseModel

class District(db.Model, BaseModel):
    __tablename__ = "districts"
    
    state_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("states.id", ondelete="RESTRICT"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0)

    state = db.relationship("State", backref="districts")

    __table_args__ = (
        db.UniqueConstraint('code', 'state_id', name='uq_district_code_state'),
        db.Index('ix_districts_state_id', 'state_id'),
    )

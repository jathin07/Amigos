from app.core.extensions import db
from app.core.base_model import BaseModel


class State(db.Model, BaseModel):
    __tablename__ = "states"

    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), nullable=False)
    country_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("countries.id"), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    display_order = db.Column(db.Integer, default=0, nullable=False)

    # Note: We enforce unique code PER COUNTRY in the service layer, not with a DB constraint here, 
    # to allow the same code in different countries if needed, though a composite unique constraint 
    # (code, country_id) could also work. We will use a UniqueConstraint to be safe.
    __table_args__ = (
        db.UniqueConstraint("code", "country_id", name="uq_state_code_country"),
    )

    # Relationships
    country = db.relationship("Country", backref=db.backref("states", lazy="dynamic"))

    def __repr__(self):
        return f"<State code={self.code} name={self.name} country_id={self.country_id}>"

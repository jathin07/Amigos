from app.core.extensions import db
from app.core.base_model import BaseModel


class Country(db.Model, BaseModel):
    __tablename__ = "countries"

    name         = db.Column(db.String(100), nullable=False)
    code         = db.Column(db.String(10),  nullable=False, unique=True, index=True)
    phone_code   = db.Column(db.String(10),  nullable=True)
    description  = db.Column(db.Text,        nullable=True)
    display_order = db.Column(db.Integer,    default=0, nullable=False)

    def __repr__(self):
        return f"<Country code={self.code} name={self.name}>"

from app.core.extensions import db
from app.core.base_model import BaseModel


class Destination(db.Model, BaseModel):
    """
    Destination master — leaf node of the geographic hierarchy.

    Hierarchy:  Country → State → District → Destination

    Business rules (enforced in service layer):
    - code is globally unique (across all destinations)
    - slug is globally unique
    - district_id.state_id must equal state_id
    - state_id.country_id   must equal country_id
    """

    __tablename__ = "destinations_master"

    # ── Core fields ───────────────────────────────────────────────
    code        = db.Column(db.String(20),  nullable=False)
    slug        = db.Column(db.String(100), nullable=False)
    name        = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text,        nullable=True)

    # ── Geographic hierarchy FKs ──────────────────────────────────
    country_id  = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("countries.id",  ondelete="RESTRICT"), nullable=False)
    state_id    = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("states.id",     ondelete="RESTRICT"), nullable=False)
    district_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("districts.id",  ondelete="RESTRICT"), nullable=False)

    # ── Media & geo ───────────────────────────────────────────────
    cover_image = db.Column(db.String(500), nullable=True)
    latitude    = db.Column(db.Numeric(10, 7), nullable=True)
    longitude   = db.Column(db.Numeric(10, 7), nullable=True)

    # ── Display ───────────────────────────────────────────────────
    display_order = db.Column(db.Integer, default=0, nullable=False)

    # ── Relationships ─────────────────────────────────────────────
    country  = db.relationship("Country",  backref=db.backref("destinations", lazy="dynamic"))
    state    = db.relationship("State",    backref=db.backref("destinations", lazy="dynamic"))
    district = db.relationship("District", backref=db.backref("destinations", lazy="dynamic"))

    # ── Constraints & Indexes ─────────────────────────────────────
    __table_args__ = (
        db.UniqueConstraint("code",         name="uq_destination_code"),
        db.UniqueConstraint("slug",         name="uq_destination_slug"),
        db.Index("ix_destination_district", "district_id"),
        db.Index("ix_destination_state",    "state_id"),
        db.Index("ix_destination_country",  "country_id"),
    )

    def __repr__(self):
        return f"<Destination code={self.code} name={self.name}>"

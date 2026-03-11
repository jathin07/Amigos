from . import db
from datetime import datetime


# -------------------------
# Destination (places catalog)
# -------------------------
class Destination(db.Model):
    __tablename__ = "destinations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    tags = db.Column(db.String(255))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    packages = db.relationship(
        "PackageDestination",
        backref="destination",
        cascade="all, delete"
    )

# -------------------------
# Travel Packages
# -------------------------
class Package(db.Model):
    __tablename__ = "packages"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)

    duration_days = db.Column(db.Integer)
    duration_nights = db.Column(db.Integer)

    price_per_person = db.Column(db.Float)
    thumbnail_url = db.Column(db.String(255))

    highlights = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    destinations = db.relationship(
        "PackageDestination",
        backref="package",
        cascade="all, delete"
    )


# -------------------------
# Package ↔ Destination relation
# (One package can have many destinations)
# -------------------------
class PackageDestination(db.Model):
    __tablename__ = "package_destinations"

    id = db.Column(db.Integer, primary_key=True)

    package_id = db.Column(
        db.Integer,
        db.ForeignKey("packages.id"),
        nullable=False
    )

    destination_id = db.Column(
        db.Integer,
        db.ForeignKey("destinations.id"),
        nullable=False
    )


# -------------------------
# Team Members (Founders / Organisers / Freelancers)
# -------------------------
class TeamMember(db.Model):
    __tablename__ = "team_members"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    role = db.Column(db.String(50))
    # founder
    # organiser
    # freelancer

    phone = db.Column(db.String(20))

    active = db.Column(db.Boolean, default=True)


# -------------------------
# Leads (Customer enquiries)
# Replaces TripRequest + QuickBooking
# -------------------------
class Lead(db.Model):
    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))

    lead_type = db.Column(db.String(20))
    # trip_request
    # quick_callback
    # package_booking

    package_id = db.Column(
        db.Integer,
        db.ForeignKey("packages.id"),
        nullable=True
    )

    travel_dates = db.Column(db.String(50))
    travelers = db.Column(db.Integer)

    budget = db.Column(db.String(50))
    notes = db.Column(db.Text)

    status = db.Column(db.String(20), default="pending")
    # pending
    # contacted
    # confirmed
    # completed

    # Who handled the lead
    contact_person_id = db.Column(
        db.Integer,
        db.ForeignKey("team_members.id")
    )

    itinerary_pdf_url = db.Column(db.String(255))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# -------------------------
# Trip Organisers
# (Multiple organisers per trip)
# -------------------------
class TripOrganizer(db.Model):
    __tablename__ = "trip_organizers"

    id = db.Column(db.Integer, primary_key=True)

    lead_id = db.Column(
        db.Integer,
        db.ForeignKey("leads.id"),
        nullable=False
    )

    team_member_id = db.Column(
        db.Integer,
        db.ForeignKey("team_members.id"),
        nullable=False
    )


# -------------------------
# Trip Finance Tracker
# Tracks revenue, costs, and profit
# -------------------------
class TripFinance(db.Model):
    __tablename__ = "trip_finance"

    id = db.Column(db.Integer, primary_key=True)

    lead_id = db.Column(
        db.Integer,
        db.ForeignKey("leads.id"),
        nullable=False
    )

    revenue = db.Column(db.Float)

    transport_cost = db.Column(db.Float)
    hotel_cost = db.Column(db.Float)
    food_cost = db.Column(db.Float)
    activity_cost = db.Column(db.Float)
    other_cost = db.Column(db.Float)

    total_cost = db.Column(db.Float)

    profit = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# -------------------------
# Admin (for authentication)
# -------------------------
class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)
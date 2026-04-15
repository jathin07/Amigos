from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


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
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


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

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


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

    preferred_destination = db.Column(db.String(255))

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
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


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

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


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
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# -------------------------
# Admin (for authentication)
# -------------------------
class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# -------------------------
# Customers 
# -------------------------
class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20), nullable=False)
    secondary_contact = db.Column(db.String(20))
    address = db.Column(db.Text)
    preferences = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# -------------------------
# Bookings 
# -------------------------
class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)

    lead_id = db.Column(db.Integer, db.ForeignKey("leads.id"), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey("packages.id"), nullable=True)

    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    total_price = db.Column(db.Float)
    status = db.Column(db.String(50), default="pending")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# -------------------------
# Travelers 
# -------------------------
class Traveler(db.Model):
    __tablename__ = "travelers"

    id = db.Column(db.Integer, primary_key=True)
    
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    id_proof = db.Column(db.String(255))
    special_requests = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# -------------------------
# Payments 
# -------------------------
class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False)
    
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100))
    status = db.Column(db.String(50), default="pending")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# -------------------------
# Tasks 
# -------------------------
class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)

    assigned_to_id = db.Column(db.Integer, db.ForeignKey("team_members.id"))
    linked_lead_id = db.Column(db.Integer, db.ForeignKey("leads.id"), nullable=True)

    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String(50), default="pending")
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
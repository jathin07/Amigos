from . import db
from datetime import datetime


# -------------------------
# Destination (places catalog)
# -------------------------
class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    tags = db.Column(db.String(100))  # e.g., hills, beach, culture


# -------------------------
# Itinerary / Package
# -------------------------
class Itinerary(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Basic Package Info
    title = db.Column(db.String(150), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    duration_nights = db.Column(db.Integer, nullable=False)
    short_description = db.Column(db.Text, nullable=False)
    thumbnail_url = db.Column(db.String(255), nullable=True)

    # Pricing
    price_per_person = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=True)

    # Highlights / Inclusions
    inclusions = db.Column(db.Text, nullable=True)   # Store as JSON or comma-separated
    exclusions = db.Column(db.Text, nullable=True)

    # Mini Itinerary Preview
    mini_itinerary = db.Column(db.Text, nullable=True)  # JSON or plain text

    # Optional PDF link (for detailed download)
    pdf_file_url = db.Column(db.String(255), nullable=True)

    # Meta Info
    created_by_admin = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# -------------------------
# Trip Requests (Plan My Trip Form)
# -------------------------
class TripRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    selected_destinations = db.Column(db.String(255))  # Comma-separated IDs for now
    travel_dates = db.Column(db.String(50))
    num_travelers = db.Column(db.Integer)
    budget_range = db.Column(db.String(50))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default="pending")  # pending/contacted/closed
    pdf_itinerary_url = db.Column(db.String(255), nullable=True)


# -------------------------
# Quick Booking (callback requests)
# -------------------------
class QuickBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    preferred_destinations = db.Column(db.String(255), nullable=True)  # Optional
    notes = db.Column(db.Text, nullable=True)  # Extra message/requirements
    preferred_time = db.Column(db.String(50), nullable=True)  # morning/evening
    status = db.Column(db.String(20), default="pending")  # pending/contacted/closed


# -------------------------
# Testimonials (for homepage)
# -------------------------
class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(100), nullable=False)   # e.g., “XYZ College”
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer)  # optional 1–5 stars
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# -------------------------
# Team Members (for homepage)
# -------------------------
class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)  # e.g., Tour Manager
    photo_url = db.Column(db.String(255))
    bio = db.Column(db.Text)  # short intro line


# -------------------------
# Admin (for authentication)
# -------------------------
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

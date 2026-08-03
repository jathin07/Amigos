import uuid
from datetime import datetime
from app.core.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import declared_attr
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON

CustomJSON = JSON().with_variant(JSONB, 'postgresql')

# -------------------------
# Mixins
# -------------------------

class BaseMixin:
    pass

class TimestampMixin(BaseMixin):
    @declared_attr
    def created_at(cls):
        return db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    @declared_attr
    def updated_at(cls):
        return db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class AuditMixin(BaseMixin):
    @declared_attr
    def created_by_team_member_id(cls):
        return db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="SET NULL"), nullable=True)

    @declared_attr
    def updated_by_team_member_id(cls):
        return db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="SET NULL"), nullable=True)

class SoftDeleteMixin(BaseMixin):
    @declared_attr
    def is_deleted(cls):
        return db.Column(db.Boolean, default=False, nullable=False)
    @declared_attr
    def deleted_at(cls):
        return db.Column(db.DateTime(timezone=True), nullable=True)
    
    @declared_attr
    def deleted_by_team_member_id(cls):
        return db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="SET NULL"), nullable=True)

class OwnershipMixin(BaseMixin):
    @declared_attr
    def owner_team_member_id(cls):
        return db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="SET NULL"), nullable=True)

class LookupMixin:
    @declared_attr
    def id(cls): return db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    @declared_attr
    def code(cls): return db.Column(db.String(50), nullable=False, unique=True)
    @declared_attr
    def name(cls): return db.Column(db.String(100), nullable=False)
    @declared_attr
    def description(cls): return db.Column(db.Text)
    @declared_attr
    def display_order(cls): return db.Column(db.Integer, default=0)
    @declared_attr
    def color(cls): return db.Column(db.String(30))
    @declared_attr
    def icon(cls): return db.Column(db.String(50))
    @declared_attr
    def is_system(cls): return db.Column(db.Boolean, default=False, nullable=False)
    @declared_attr
    def is_active(cls): return db.Column(db.Boolean, default=True, nullable=False)


# -------------------------
# Lookups
# -------------------------

class OrganizationType(db.Model, LookupMixin):
    __tablename__ = "organization_types"

class VendorType(db.Model, LookupMixin):
    __tablename__ = "vendor_types"

class Department(db.Model, LookupMixin):
    __tablename__ = "departments"

class Role(db.Model, LookupMixin):
    __tablename__ = "roles"

class TripType(db.Model, LookupMixin):
    __tablename__ = "trip_types"

class LeadStatus(db.Model, LookupMixin):
    __tablename__ = "lead_statuses"

class LeadSource(db.Model, LookupMixin):
    __tablename__ = "lead_sources"

class LeadPriority(db.Model, LookupMixin):
    __tablename__ = "lead_priorities"

class LeadLostReason(db.Model, LookupMixin):
    __tablename__ = "lead_lost_reasons"

class CRMActivityType(db.Model, LookupMixin):
    __tablename__ = "crm_activity_types"

class ProposalStatus(db.Model, LookupMixin):
    __tablename__ = "proposal_statuses"

class BookingStatus(db.Model, LookupMixin):
    __tablename__ = "booking_statuses"

class BookingSource(db.Model, LookupMixin):
    __tablename__ = "booking_sources"

class RefundStatus(db.Model, LookupMixin):
    __tablename__ = "refund_statuses"

class PaymentMethod(db.Model, LookupMixin):
    __tablename__ = "payment_methods"

class PaymentStatus(db.Model, LookupMixin):
    __tablename__ = "payment_statuses"

class PaymentType(db.Model, LookupMixin):
    __tablename__ = "payment_types"

class DocumentType(db.Model, LookupMixin):
    __tablename__ = "document_types"

class TripPlanStatus(db.Model, LookupMixin):
    __tablename__ = "trip_plan_statuses"

class VendorAllocationStatus(db.Model, LookupMixin):
    __tablename__ = "vendor_allocation_statuses"

class ExpenseCategory(db.Model, LookupMixin):
    __tablename__ = "expense_categories"

class ExpenseType(db.Model, LookupMixin):
    __tablename__ = "expense_types"

class TaskStatus(db.Model, LookupMixin):
    __tablename__ = "task_statuses"

class TaskPriority(db.Model, LookupMixin):
    __tablename__ = "task_priorities"

class BookingType(db.Model, LookupMixin):
    __tablename__ = "booking_types"

class NotificationPriority(db.Model, LookupMixin):
    __tablename__ = "notification_priorities"

class FollowUpType(db.Model, LookupMixin):
    __tablename__ = "followup_types"


# -------------------------
# Master Module
# -------------------------

class SystemSetting(db.Model, TimestampMixin, AuditMixin):
    __tablename__ = "system_settings"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = db.Column(db.String(100), nullable=False, unique=True)
    value = db.Column(CustomJSON, nullable=False)
    description = db.Column(db.Text)

class Organization(db.Model, TimestampMixin, AuditMixin, SoftDeleteMixin):
    __tablename__ = "organizations"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_name = db.Column(db.String(200), nullable=False)
    organization_type_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("organization_types.id", ondelete="RESTRICT"), nullable=False)
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(150))
    website = db.Column(db.String(200))
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    divisions = db.relationship("OrganizationDivision", backref="organization", cascade="all, delete-orphan", lazy=True)
    contact_persons = db.relationship("ContactPerson", backref="organization", cascade="all, delete-orphan", lazy=True)

class OrganizationDivision(db.Model, TimestampMixin, AuditMixin):
    __tablename__ = "organization_divisions"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    department = db.Column(db.String(150))
    course = db.Column(db.String(150))
    section = db.Column(db.String(50))
    year = db.Column(db.String(50))
    semester = db.Column(db.String(50))
    batch = db.Column(db.String(50))

class ContactPerson(db.Model, TimestampMixin, AuditMixin, SoftDeleteMixin):
    __tablename__ = "contact_persons"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True)
    name = db.Column(db.String(150), nullable=False)
    designation = db.Column(db.String(100))
    phone = db.Column(db.String(20), nullable=False)
    alternate_phone = db.Column(db.String(20))
    email = db.Column(db.String(150))
    is_primary = db.Column(db.Boolean, default=False, nullable=False)
    preferred_contact_method = db.Column(db.String(30))
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

class Vendor(db.Model, TimestampMixin, AuditMixin, SoftDeleteMixin):
    __tablename__ = "vendors"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_name = db.Column(db.String(200), nullable=False)
    vendor_type_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("vendor_types.id", ondelete="RESTRICT"), nullable=False)
    contact_person = db.Column(db.String(150))
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(150))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    service_area = db.Column(db.String(255))
    internal_rating = db.Column(db.Integer)
    bank_account_name = db.Column(db.String(150))
    bank_account_number = db.Column(db.String(50))
    ifsc = db.Column(db.String(20))
    gst_number = db.Column(db.String(20))
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    verified_at = db.Column(db.DateTime(timezone=True))
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    version = db.Column(db.Integer, default=1, nullable=False)

class Destination(db.Model, TimestampMixin, AuditMixin, SoftDeleteMixin):
    __tablename__ = "destinations"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(150), nullable=False)
    district = db.Column(db.String(100))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    thumbnail_url = db.Column(db.Text)
    best_season = db.Column(db.String(100))
    tags = db.Column(CustomJSON)
    latitude = db.Column(db.Numeric(12, 6))
    longitude = db.Column(db.Numeric(12, 6))
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    images = db.relationship("DestinationImage", backref="destination", cascade="all, delete-orphan", lazy=True)

class DestinationImage(db.Model, TimestampMixin, AuditMixin):
    __tablename__ = "destination_images"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    destination_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    display_order = db.Column(db.Integer)
    caption = db.Column(db.String(255))
    is_cover = db.Column(db.Boolean, default=False, nullable=False)

class Package(db.Model, TimestampMixin, AuditMixin, SoftDeleteMixin):
    __tablename__ = "packages"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duration_days = db.Column(db.Integer, nullable=False)
    duration_nights = db.Column(db.Integer, nullable=False)
    starting_price = db.Column(db.Numeric(12, 2))
    starting_city = db.Column(db.String(100))
    thumbnail_url = db.Column(db.Text)
    terms = db.Column(db.Text)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    version = db.Column(db.Integer, nullable=False, default=1)

    images = db.relationship("PackageImage", backref="package", cascade="all, delete-orphan", lazy=True)
    highlights = db.relationship("PackageHighlight", backref="package", cascade="all, delete-orphan", lazy=True)
    inclusions = db.relationship("PackageInclusion", backref="package", cascade="all, delete-orphan", lazy=True)
    exclusions = db.relationship("PackageExclusion", backref="package", cascade="all, delete-orphan", lazy=True)
    destinations = db.relationship("PackageDestination", backref="package", cascade="all, delete-orphan", lazy=True)

class PackageImage(db.Model, TimestampMixin, AuditMixin):
    __tablename__ = "package_images"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("packages.id", ondelete="CASCADE"), nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    display_order = db.Column(db.Integer)
    caption = db.Column(db.String(255))
    is_cover = db.Column(db.Boolean, default=False, nullable=False)

class PackageHighlight(db.Model, TimestampMixin, AuditMixin):
    __tablename__ = "package_highlights"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("packages.id", ondelete="CASCADE"), nullable=False)
    highlight_text = db.Column(db.Text, nullable=False)
    display_order = db.Column(db.Integer)

class PackageInclusion(db.Model, TimestampMixin, AuditMixin):
    __tablename__ = "package_inclusions"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("packages.id", ondelete="CASCADE"), nullable=False)
    inclusion_text = db.Column(db.Text, nullable=False)

class PackageExclusion(db.Model, TimestampMixin, AuditMixin):
    __tablename__ = "package_exclusions"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("packages.id", ondelete="CASCADE"), nullable=False)
    exclusion_text = db.Column(db.Text, nullable=False)

class PackageDestination(db.Model, TimestampMixin, AuditMixin):
    __tablename__ = "package_destinations"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("packages.id", ondelete="CASCADE"), nullable=False)
    destination_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("destinations.id", ondelete="RESTRICT"), nullable=False)
    day_order = db.Column(db.Integer)
    sequence = db.Column(db.Integer)
    overnight_stay = db.Column(db.Boolean, default=False, nullable=False)
    default_duration = db.Column(db.String(50))

class ChecklistTemplate(db.Model, TimestampMixin, AuditMixin, SoftDeleteMixin):
    __tablename__ = "checklist_templates"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_name = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

class TeamMember(db.Model, TimestampMixin, AuditMixin, SoftDeleteMixin):
    __tablename__ = "team_members"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100))
    display_name = db.Column(db.String(150), nullable=False)
    avatar_url = db.Column(db.Text)
    dob = db.Column(db.Date)
    gender = db.Column(db.String(20))
    
    employee_code = db.Column(db.String(50), unique=True)
    official_email = db.Column(db.String(150))
    personal_email = db.Column(db.String(150))
    phone = db.Column(db.String(20), nullable=False)
    designation = db.Column(db.String(100))
    
    department_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("departments.id", ondelete="RESTRICT"), nullable=True)
    role_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("roles.id", ondelete="RESTRICT"), nullable=True)
    reporting_manager_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="SET NULL"), nullable=True)
    
    employment_status = db.Column(db.String(50))
    availability_status = db.Column(db.String(50), default='AVAILABLE')
    joined_date = db.Column(db.Date)
    left_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    version = db.Column(db.Integer, default=1, nullable=False)

    emergency_contact_name = db.Column(db.String(150))
    emergency_contact_phone = db.Column(db.String(20))

    role = db.relationship("Role")
    department = db.relationship("Department")
    manager = db.relationship("TeamMember", remote_side=[id], foreign_keys=[reporting_manager_id])
    user_account = db.relationship("UserAccount", backref="team_member", uselist=False, lazy=True)


# -------------------------
# Auth Module
# -------------------------

class UserAccount(db.Model, TimestampMixin):
    __tablename__ = "user_accounts"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_member_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="CASCADE"), unique=True, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    
    password_hash = db.Column(db.String(255), nullable=False)
    password_algorithm = db.Column(db.String(50), default="bcrypt")
    password_hash_version = db.Column(db.Integer, default=1)
    
    last_password_change = db.Column(db.DateTime(timezone=True))
    must_change_password = db.Column(db.Boolean, default=False, nullable=False)
    
    last_login_at = db.Column(db.DateTime(timezone=True))
    last_login_ip = db.Column(db.String(45))
    last_login_device = db.Column(db.String(255))
    
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    last_failed_login = db.Column(db.DateTime(timezone=True))
    locked_until = db.Column(db.DateTime(timezone=True))
    is_email_verified = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    reset_token_hash = db.Column(db.String(255))
    reset_token_expires_at = db.Column(db.DateTime(timezone=True))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class RefreshToken(db.Model, TimestampMixin):
    __tablename__ = "refresh_tokens"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_account_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("user_accounts.id", ondelete="CASCADE"), nullable=False)
    token_hash = db.Column(db.String(255), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    is_revoked = db.Column(db.Boolean, default=False, nullable=False)

class PasswordResetToken(db.Model, TimestampMixin):
    __tablename__ = "password_reset_tokens"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_account_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("user_accounts.id", ondelete="CASCADE"), nullable=False)
    token_hash = db.Column(db.String(255), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    is_used = db.Column(db.Boolean, default=False, nullable=False)

class LoginHistory(db.Model):
    __tablename__ = "login_history"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_account_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("user_accounts.id", ondelete="CASCADE"), nullable=False)
    login_method = db.Column(db.String(50), nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    browser = db.Column(db.String(50))
    os = db.Column(db.String(50))
    device = db.Column(db.String(50))
    device_id = db.Column(db.String(100))
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    
    login_time = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    logout_time = db.Column(db.DateTime(timezone=True))
    session_duration = db.Column(db.Integer)
    logout_reason = db.Column(db.String(50))
    
    is_success = db.Column(db.Boolean, nullable=False)
    failure_reason = db.Column(db.String(255))


# -------------------------
# CRM Module
# -------------------------

class Customer(db.Model, TimestampMixin, AuditMixin, SoftDeleteMixin):
    __tablename__ = "customers"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=True)
    primary_contact_person_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("contact_persons.id", ondelete="RESTRICT"), nullable=True)
    customer_type = db.Column(db.String(30), nullable=False, default='B2C')
    preferences = db.Column(db.Text)
    emergency_contact = db.Column(db.String(20))
    preferred_contact_time = db.Column(db.String(100))
    remarks = db.Column(db.Text)
    customer_since = db.Column(db.Date)
    
    organization = db.relationship("Organization")
    bookings = db.relationship("Booking", backref="customer", lazy=True)

class Lead(db.Model, TimestampMixin, AuditMixin, SoftDeleteMixin, OwnershipMixin):
    __tablename__ = "leads"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_number = db.Column(db.String(30), unique=True, nullable=False)
    lead_source_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("lead_sources.id", ondelete="RESTRICT"), nullable=False)
    contact_person_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("contact_persons.id", ondelete="RESTRICT"), nullable=False)
    organization_division_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("organization_divisions.id", ondelete="SET NULL"), nullable=True)
    package_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("packages.id", ondelete="SET NULL"), nullable=True)
    trip_type_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("trip_types.id", ondelete="RESTRICT"), nullable=True)
    priority_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("lead_priorities.id", ondelete="RESTRICT"), nullable=True)
    travel_start_date = db.Column(db.Date)
    travel_end_date = db.Column(db.Date)
    estimated_trip_days = db.Column(db.Integer)
    estimated_trip_nights = db.Column(db.Integer)
    traveler_count = db.Column(db.Integer, nullable=False, default=1)
    male_count = db.Column(db.Integer)
    female_count = db.Column(db.Integer)
    faculty_count = db.Column(db.Integer)
    budget = db.Column(db.Numeric(12, 2))
    notes = db.Column(db.Text)
    current_status_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("lead_statuses.id", ondelete="RESTRICT"), nullable=False)
    expected_travel_date = db.Column(db.Date)
    lost_reason_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("lead_lost_reasons.id", ondelete="RESTRICT"), nullable=True)
    lost_date = db.Column(db.Date)
    version = db.Column(db.Integer, nullable=False, default=1)

    lead_destinations = db.relationship("LeadDestination", backref="lead", cascade="all, delete-orphan", lazy=True)
    activities = db.relationship("CRMActivity", backref="lead", cascade="all, delete-orphan", lazy=True)
    follow_ups = db.relationship("FollowUp", backref="lead", cascade="all, delete-orphan", lazy=True)
    proposals = db.relationship("Proposal", backref="lead", cascade="all, delete-orphan", lazy=True)
    booking = db.relationship("Booking", backref="lead", uselist=False, lazy=True)
    documents = db.relationship("Document", backref="lead", foreign_keys="[Document.lead_id]", cascade="all, delete-orphan", lazy=True)

    contact_person = db.relationship("ContactPerson", foreign_keys=[contact_person_id], lazy=True)
    current_status = db.relationship("LeadStatus", foreign_keys=[current_status_id], lazy=True)
    lead_source = db.relationship("LeadSource", foreign_keys=[lead_source_id], lazy=True)
    priority = db.relationship("LeadPriority", foreign_keys=[priority_id], lazy=True)
    trip_type = db.relationship("TripType", foreign_keys=[trip_type_id], lazy=True)
    lost_reason = db.relationship("LeadLostReason", foreign_keys=[lost_reason_id], lazy=True)
    package = db.relationship("Package", foreign_keys=[package_id], lazy=True)

    __table_args__ = (
        db.Index("idx_lead_number", "lead_number", unique=True),
        db.Index("idx_lead_status", "current_status_id"),
        db.Index("idx_lead_owner", "owner_team_member_id"),
        db.Index("idx_lead_expected_travel", "expected_travel_date"),
        db.Index("idx_lead_active", "lead_number", postgresql_where=(db.column('is_deleted') == False)),
    )

class LeadDestination(db.Model):
    __tablename__ = "lead_destinations"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    destination_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("destinations.id", ondelete="RESTRICT"), nullable=False)
    priority = db.Column(db.String(50))
    day_preference = db.Column(db.String(50))

    destination = db.relationship(Destination, foreign_keys=[destination_id], lazy=True)

class CRMActivity(db.Model, TimestampMixin, AuditMixin):
    __tablename__ = "crm_activities"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    activity_type_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("crm_activity_types.id", ondelete="RESTRICT"), nullable=False)
    activity_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    discussion_summary = db.Column(db.Text, nullable=False)
    outcome = db.Column(db.Text)
    next_action = db.Column(db.Text)
    next_followup_date = db.Column(db.Date)

    activity_type = db.relationship("CRMActivityType", foreign_keys=[activity_type_id], lazy=True)

class FollowUp(db.Model, TimestampMixin, AuditMixin, OwnershipMixin, SoftDeleteMixin):
    __tablename__ = "follow_ups"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    followup_type_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("followup_types.id", ondelete="RESTRICT"), nullable=False)
    scheduled_date = db.Column(db.DateTime(timezone=True), nullable=False)
    notes = db.Column(db.Text)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime(timezone=True))

    followup_type = db.relationship("FollowUpType", foreign_keys=[followup_type_id], lazy=True)


# -------------------------
# Proposal Module
# -------------------------

class Proposal(db.Model, TimestampMixin, AuditMixin, SoftDeleteMixin):
    __tablename__ = "proposals"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    row_version = db.Column(db.Integer, default=1, nullable=False)
    proposal_title = db.Column(db.String(200), nullable=False)
    price_per_person = db.Column(db.Numeric(12, 2))
    total_amount = db.Column(db.Numeric(12, 2))
    pdf_url = db.Column(db.Text)
    internal_notes = db.Column(db.Text)
    structured_itinerary = db.Column(CustomJSON)
    revision_reason = db.Column(db.Text)
    sent_date = db.Column(db.Date)
    approved_date = db.Column(db.Date)
    valid_until = db.Column(db.Date)
    approved_by_team_member_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="SET NULL"), nullable=True)
    is_final = db.Column(db.Boolean, default=False, nullable=False)
    status_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("proposal_statuses.id", ondelete="RESTRICT"), nullable=False)
    
    status = db.relationship("ProposalStatus", foreign_keys=[status_id], lazy=True)
    approved_by = db.relationship("TeamMember", foreign_keys=[approved_by_team_member_id], lazy=True)
    destinations = db.relationship("ProposalDestination", backref="proposal", cascade="all, delete-orphan", lazy=True)

    __table_args__ = (
        db.UniqueConstraint("lead_id", "version", name="uq_proposal_lead_version"),
        db.Index(
            "uq_proposal_lead_final",
            "lead_id",
            unique=True,
            sqlite_where=(db.column('is_final') == True),
            postgresql_where=(db.column('is_final') == True)
        )
    )

class ProposalDestination(db.Model):
    __tablename__ = "proposal_destinations"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proposal_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False)
    destination_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("destinations.id", ondelete="RESTRICT"), nullable=False)
    day_order = db.Column(db.Integer)
    sequence_no = db.Column(db.Integer)
    overnight_stay = db.Column(db.Boolean, default=False, nullable=False)
    
    day_title = db.Column(db.String(150))
    travel_time = db.Column(db.String(100))
    travel_mode = db.Column(db.String(100))
    distance = db.Column(db.Numeric(12, 2))
    notes = db.Column(db.Text)

    destination = db.relationship(Destination, foreign_keys=[destination_id], lazy=True)



# -------------------------
# Booking Module
# -------------------------

class Booking(db.Model, TimestampMixin, AuditMixin, SoftDeleteMixin, OwnershipMixin):
    __tablename__ = "bookings"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_number = db.Column(db.String(30), unique=True, nullable=False)
    row_version = db.Column(db.Integer, default=1, nullable=False)
    entry_mode = db.Column(db.String(30), nullable=False, default='NORMAL')
    booking_type_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("booking_types.id", ondelete="RESTRICT"), nullable=False)
    group_name = db.Column(db.String(200))
    booking_source_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("booking_sources.id", ondelete="RESTRICT"), nullable=False)
    lead_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("leads.id", ondelete="RESTRICT"), nullable=True)
    customer_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False)
    proposal_version_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("proposals.id", ondelete="RESTRICT"), unique=True, nullable=True)
    booking_status_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("booking_statuses.id", ondelete="RESTRICT"), nullable=False)
    contact_person_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("contact_persons.id", ondelete="SET NULL"), nullable=True)
    
    trip_coordinator_team_member_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="SET NULL"), nullable=True)
    confirmed_by_team_member_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="SET NULL"), nullable=True)
    completed_by_team_member_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="SET NULL"), nullable=True)
    cancelled_by_team_member_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="SET NULL"), nullable=True)
    closed_by_team_member_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="SET NULL"), nullable=True)
    
    package_name_snapshot = db.Column(db.String(150))
    organization_name_snapshot = db.Column(db.String(150))
    contact_person_snapshot = db.Column(db.String(150))
    trip_name_snapshot = db.Column(db.String(200))
    
    previous_booking_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True)
    booking_date = db.Column(db.Date, nullable=False)
    trip_start_date = db.Column(db.Date, nullable=False)
    trip_end_date = db.Column(db.Date, nullable=False)
    total_travelers = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    
    booking_created_at = db.Column(db.DateTime(timezone=True))
    confirmed_at = db.Column(db.DateTime(timezone=True))
    completed_at = db.Column(db.DateTime(timezone=True))
    closed_at = db.Column(db.DateTime(timezone=True))
    cancelled_at = db.Column(db.DateTime(timezone=True))
    
    cancellation_reason = db.Column(db.Text)
    internal_notes = db.Column(db.Text)

    travelers = db.relationship("Traveler", backref="booking", cascade="all, delete-orphan", lazy=True)
    payments = db.relationship("Payment", backref="booking", cascade="all, delete-orphan", lazy=True)
    documents = db.relationship("Document", backref="booking", foreign_keys="[Document.booking_id]", cascade="all, delete-orphan", lazy=True)
    trip_plan = db.relationship("TripPlan", backref="booking", uselist=False, cascade="all, delete-orphan", lazy=True)
    tasks = db.relationship("Task", backref="booking", cascade="all, delete-orphan", lazy=True)
    checklists = db.relationship("Checklist", backref="booking", cascade="all, delete-orphan", lazy=True)
    expenses = db.relationship("Expense", backref="booking", cascade="all, delete-orphan", lazy=True)
    payment_schedules = db.relationship("PaymentSchedule", backref="booking", cascade="all, delete-orphan", lazy=True)
    status_history = db.relationship("BookingStatusHistory", backref="booking", cascade="all, delete-orphan", lazy=True)
    refunds = db.relationship("Refund", backref="booking", cascade="all, delete-orphan", lazy=True)
    previous_booking = db.relationship("Booking", remote_side=[id], backref=db.backref("next_bookings", lazy=True))

    status = db.relationship("BookingStatus", foreign_keys=[booking_status_id], lazy=True)
    booking_source = db.relationship("BookingSource", foreign_keys=[booking_source_id], lazy=True)
    booking_type = db.relationship("BookingType", foreign_keys=[booking_type_id], lazy=True)
    trip_coordinator = db.relationship("TeamMember", foreign_keys=[trip_coordinator_team_member_id], lazy=True)

    __table_args__ = (
        db.CheckConstraint("trip_end_date >= trip_start_date", name="chk_booking_trip_dates"),
        db.Index("idx_booking_number", "booking_number", unique=True),
        db.Index("idx_booking_status", "booking_status_id"),
        db.Index("idx_booking_trip_start", "trip_start_date"),
        db.Index("idx_booking_customer", "customer_id"),
        db.Index("idx_booking_active", "booking_number", postgresql_where=(db.column('is_deleted') == False)),
    )

    @property
    def customer_revenue(self):
        return sum(p.amount for p in self.payments if p.payment_status and p.payment_status.code == "RECEIVED")

    @property
    def pending_customer_balance(self):
        return self.total_amount - self.customer_revenue

    @property
    def vendor_cost(self):
        cost = 0
        if self.trip_plan:
            for day in self.trip_plan.trip_days:
                for alloc in day.vendor_allocations:
                    cost += alloc.total_paid
        return cost

    @property
    def operational_expense(self):
        return sum(e.amount for e in self.expenses if e.expense_type and e.expense_type.code != "VENDOR_PAYMENT")

    @property
    def total_cost(self):
        return self.vendor_cost + self.operational_expense

    @property
    def net_profit(self):
        return self.customer_revenue - self.total_cost

    @property
    def profit_percentage(self):
        rev = self.customer_revenue
        if not rev:
            return 0
        return (self.net_profit / rev) * 100

class Traveler(db.Model, TimestampMixin, AuditMixin, SoftDeleteMixin):
    __tablename__ = "travelers"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    id_proof_type = db.Column(db.String(50))
    id_proof_number = db.Column(db.String(100))
    emergency_contact = db.Column(db.String(20))
    special_requirements = db.Column(db.Text)
    is_group_leader = db.Column(db.Boolean, default=False, nullable=False)

    documents = db.relationship("Document", backref="traveler", foreign_keys="[Document.traveler_id]", cascade="all, delete-orphan", lazy=True)

    __table_args__ = (
        db.CheckConstraint("age >= 0", name="chk_traveler_age"),
    )

class Document(db.Model, TimestampMixin, AuditMixin):
    __tablename__ = "documents"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=True)
    lead_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("leads.id", ondelete="CASCADE"), nullable=True)
    vendor_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("vendors.id", ondelete="CASCADE"), nullable=True)
    organization_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True)
    traveler_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("travelers.id", ondelete="CASCADE"), nullable=True)
    document_type_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("document_types.id", ondelete="RESTRICT"), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_url = db.Column(db.Text, nullable=False)
    storage_provider = db.Column(db.String(50))
    storage_key = db.Column(db.String(255))

    document_type = db.relationship("DocumentType", foreign_keys=[document_type_id], lazy=True)

    __table_args__ = (
        db.CheckConstraint(
            "(CASE WHEN booking_id IS NULL THEN 0 ELSE 1 END + "
            "CASE WHEN lead_id IS NULL THEN 0 ELSE 1 END + "
            "CASE WHEN vendor_id IS NULL THEN 0 ELSE 1 END + "
            "CASE WHEN organization_id IS NULL THEN 0 ELSE 1 END + "
            "CASE WHEN traveler_id IS NULL THEN 0 ELSE 1 END) = 1",
            name="chk_document_single_parent"
        ),
    )

class BookingStatusHistory(db.Model, TimestampMixin, AuditMixin):
    __tablename__ = "booking_status_history"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    from_status_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("booking_statuses.id", ondelete="RESTRICT"), nullable=True)
    to_status_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("booking_statuses.id", ondelete="RESTRICT"), nullable=False)
    changed_by_team_member_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="SET NULL"), nullable=True)
    notes = db.Column(db.Text)

    from_status = db.relationship("BookingStatus", foreign_keys=[from_status_id], lazy=True)
    to_status = db.relationship("BookingStatus", foreign_keys=[to_status_id], lazy=True)
    changed_by = db.relationship("TeamMember", foreign_keys=[changed_by_team_member_id], lazy=True)

class PaymentSchedule(db.Model, TimestampMixin, AuditMixin):
    __tablename__ = "payment_schedules"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    installment_no = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    percentage = db.Column(db.Numeric(5, 2))
    payment_status_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("payment_statuses.id", ondelete="RESTRICT"), nullable=False)
    remarks = db.Column(db.Text)

    payment_status = db.relationship("PaymentStatus", foreign_keys=[payment_status_id], lazy=True)

    __table_args__ = (
        db.CheckConstraint("amount > 0", name="chk_payment_schedule_amount"),
        db.CheckConstraint("percentage >= 0 AND percentage <= 100", name="chk_payment_schedule_percentage"),
    )


# -------------------------
# Operations Module
# -------------------------

class TripPlan(db.Model, TimestampMixin, AuditMixin):
    __tablename__ = "trip_plans"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    version = db.Column(db.Integer, nullable=False, default=1)
    row_version = db.Column(db.Integer, default=1, nullable=False)
    is_final = db.Column(db.Boolean, default=True, nullable=False)
    prepared_by_team_member_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="SET NULL"), nullable=False)
    prepared_date = db.Column(db.Date, nullable=False)
    approved_by_team_member_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="SET NULL"), nullable=True)
    approved_at = db.Column(db.DateTime(timezone=True))
    final_itinerary_pdf = db.Column(db.Text)
    notes = db.Column(db.Text)
    status_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("trip_plan_statuses.id", ondelete="RESTRICT"), nullable=False)
    trip_plan_type = db.Column(db.String(50), default='MANUAL', nullable=False)

    trip_days = db.relationship("TripDay", backref="trip_plan", cascade="all, delete-orphan", lazy=True)

    __table_args__ = (
        db.UniqueConstraint("booking_id", "version", name="uq_trip_plan_booking_version"),
        db.Index("uq_trip_plan_booking_final", "booking_id", unique=True, postgresql_where=(db.column('is_final') == True))
    )

class TripDay(db.Model):
    __tablename__ = "trip_days"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_plan_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("trip_plans.id", ondelete="CASCADE"), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    start_location = db.Column(db.String(100))
    end_location = db.Column(db.String(100))
    overnight_destination_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("destinations.id", ondelete="RESTRICT"), nullable=True)
    start_time = db.Column(db.String(50))
    end_time = db.Column(db.String(50))
    morning_plan = db.Column(db.Text)
    afternoon_plan = db.Column(db.Text)
    evening_plan = db.Column(db.Text)
    night_stay = db.Column(db.String(150))
    notes = db.Column(db.Text)

    vendor_allocations = db.relationship("VendorAllocation", backref="trip_day", cascade="all, delete-orphan", lazy=True)

class VendorAllocation(db.Model, TimestampMixin, AuditMixin, OwnershipMixin):
    __tablename__ = "vendor_allocations"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_day_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("trip_days.id", ondelete="CASCADE"), nullable=False)
    vendor_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("vendors.id", ondelete="RESTRICT"), nullable=False)
    service_name = db.Column(db.String(150), nullable=False)
    service_type_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("vendor_types.id", ondelete="RESTRICT"), nullable=False)
    service_date = db.Column(db.Date)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    quoted_amount = db.Column(db.Numeric(12, 2), nullable=False)
    confirmed_price = db.Column(db.Numeric(12, 2), nullable=True)
    vendor_name_snapshot = db.Column(db.String(150))
    vendor_phone_snapshot = db.Column(db.String(20))
    vendor_address_snapshot = db.Column(db.Text)
    vendor_service_snapshot = db.Column(CustomJSON)
    allocation_status_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("vendor_allocation_statuses.id", ondelete="RESTRICT"), nullable=False)
    confirmed_by_team_member_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="SET NULL"), nullable=True)
    confirmed_at = db.Column(db.DateTime(timezone=True))
    is_locked = db.Column(db.Boolean, default=False, nullable=False)
    notes = db.Column(db.Text)

    vendor_payments = db.relationship("VendorPayment", backref="vendor_allocation", cascade="all, delete-orphan", lazy=True)
    expenses = db.relationship("Expense", backref="vendor_allocation", lazy=True)

    @property
    def total_paid(self):
        return sum(vp.amount for vp in self.vendor_payments if vp.payment_status and vp.payment_status.code == "RECEIVED")

    @property
    def balance_due(self):
        return self.quoted_amount - self.total_paid

    @property
    def settlement_status(self):
        paid = self.total_paid
        if paid == 0:
            return "PENDING"
        elif paid < self.quoted_amount:
            return "PARTIAL"
        return "SETTLED"

class Task(db.Model, TimestampMixin, AuditMixin, SoftDeleteMixin, OwnershipMixin):
    __tablename__ = "tasks"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=True)
    lead_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("leads.id", ondelete="CASCADE"), nullable=True)
    assigned_to_team_member_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="RESTRICT"), nullable=False)
    assigned_by_team_member_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="SET NULL"), nullable=True)
    parent_task_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    task_status_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("task_statuses.id", ondelete="RESTRICT"), nullable=False)
    priority_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("task_priorities.id", ondelete="RESTRICT"), nullable=False)
    estimated_hours = db.Column(db.Numeric(12, 2))
    actual_hours = db.Column(db.Numeric(12, 2))
    
    subtasks = db.relationship("Task", backref=db.backref('parent_task', remote_side=[id]), lazy=True)

    __table_args__ = (
        db.Index("idx_task_assigned_to", "assigned_to_team_member_id"),
        db.Index("idx_task_due_date", "due_date"),
        db.Index("idx_task_status", "task_status_id"),
    )

class Checklist(db.Model, TimestampMixin, AuditMixin):
    __tablename__ = "checklists"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    template_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("checklist_templates.id", ondelete="RESTRICT"), nullable=True)
    item_name = db.Column(db.String(200), nullable=False)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime(timezone=True))


# -------------------------
# Finance Module
# -------------------------

class Payment(db.Model, TimestampMixin, AuditMixin):
    __tablename__ = "payments"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    payment_schedule_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("payment_schedules.id", ondelete="RESTRICT"), nullable=True)
    payment_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_method_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("payment_methods.id", ondelete="RESTRICT"), nullable=False)
    payment_status_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("payment_statuses.id", ondelete="RESTRICT"), nullable=False)
    payment_type_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("payment_types.id", ondelete="RESTRICT"), nullable=False)
    installment_no = db.Column(db.Integer)
    transaction_reference = db.Column(db.String(100))
    receipt_url = db.Column(db.Text)
    remarks = db.Column(db.Text)
    received_by_team_member_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="SET NULL"), nullable=True)
    verified_by_team_member_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="SET NULL"), nullable=True)

    payment_status = db.relationship("PaymentStatus")

    __table_args__ = (
        db.Index("idx_payment_booking", "booking_id"),
        db.Index("idx_payment_status", "payment_status_id"),
        db.Index("idx_payment_date", "payment_date"),
        db.CheckConstraint("amount > 0", name="chk_payment_amount"),
    )

class VendorPayment(db.Model, TimestampMixin, AuditMixin):
    __tablename__ = "vendor_payments"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_allocation_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("vendor_allocations.id", ondelete="CASCADE"), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_method_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("payment_methods.id", ondelete="RESTRICT"), nullable=False)
    payment_status_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("payment_statuses.id", ondelete="RESTRICT"), nullable=False)
    transaction_reference = db.Column(db.String(100))
    receipt_url = db.Column(db.Text)
    internal_notes = db.Column(db.Text)

    payment_status = db.relationship("PaymentStatus")

    __table_args__ = (
        db.CheckConstraint("amount > 0", name="chk_vendor_payment_amount"),
    )

class Expense(db.Model, TimestampMixin, AuditMixin):
    __tablename__ = "expenses"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    vendor_allocation_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("vendor_allocations.id", ondelete="CASCADE"), nullable=True)
    vendor_payment_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("vendor_payments.id", ondelete="SET NULL"), nullable=True)
    expense_category_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("expense_categories.id", ondelete="RESTRICT"), nullable=False)
    expense_type_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("expense_types.id", ondelete="RESTRICT"), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    expense_date = db.Column(db.Date, nullable=False)
    expense_description = db.Column(db.String(255))
    remarks = db.Column(db.Text)
    approved_by_team_member_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="SET NULL"), nullable=True)
    
    expense_type = db.relationship("ExpenseType")

    __table_args__ = (
        db.CheckConstraint("amount > 0", name="chk_expense_amount"),
    )

class Refund(db.Model, TimestampMixin, AuditMixin):
    __tablename__ = "refunds"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    refund_status_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("refund_statuses.id", ondelete="RESTRICT"), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    refund_date = db.Column(db.Date)
    payment_method_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("payment_methods.id", ondelete="RESTRICT"), nullable=False)
    transaction_reference = db.Column(db.String(100))
    remarks = db.Column(db.Text)

    __table_args__ = (
        db.CheckConstraint("amount > 0", name="chk_refund_amount"),
    )


# -------------------------
# Assignment Module
# -------------------------

class AssignmentHistory(db.Model, TimestampMixin, AuditMixin):
    __tablename__ = "assignment_history"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Uuid(as_uuid=True), nullable=False)
    assignment_type = db.Column(db.String(50), nullable=False)
    previous_team_member_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="SET NULL"), nullable=True)
    new_team_member_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="SET NULL"), nullable=True)
    reason = db.Column(db.Text)
    changed_by_team_member_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="SET NULL"), nullable=True)
    effective_from = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    effective_to = db.Column(db.DateTime(timezone=True))
    entity_status = db.Column(db.String(50))

    previous_team_member = db.relationship("TeamMember", foreign_keys=[previous_team_member_id], lazy=True)
    new_team_member = db.relationship("TeamMember", foreign_keys=[new_team_member_id], lazy=True)


# -------------------------
# Notification Module
# -------------------------

class Notification(db.Model, TimestampMixin):
    __tablename__ = "notifications"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_member_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="CASCADE"), nullable=False)
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Uuid(as_uuid=True))
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    action_url = db.Column(db.String(255))
    notification_type = db.Column(db.String(50))
    priority_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("notification_priorities.id", ondelete="RESTRICT"), nullable=False)
    sent_at = db.Column(db.DateTime(timezone=True))
    read_at = db.Column(db.DateTime(timezone=True))

    __table_args__ = (
        db.Index("idx_notification_team_member", "team_member_id"),
        db.Index("idx_notification_read_at", "read_at"),
    )

class AuditLog(db.Model, TimestampMixin):
    __tablename__ = "audit_logs"
    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_member_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("team_members.id", ondelete="SET NULL"), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    table_name = db.Column(db.String(100), nullable=False)
    entity_id = db.Column(db.Uuid(as_uuid=True), nullable=False)
    old_values = db.Column(CustomJSON)
    new_values = db.Column(CustomJSON)
    ip_address = db.Column(db.String(45))
    request_id = db.Column(db.String(100))
    endpoint = db.Column(db.String(255))
    http_method = db.Column(db.String(10))
 
# Phase 1: Foundation Masters
from app.modules.master.destination.models import Destination
from app.modules.master.city.models import City
from app.modules.master.models import (
    PackageCategory,
    HotelCategory,
    MealPlan,
    VehicleType,
    ActivityType,
    Season,
    PaymentMethod,
    Currency,
    CancellationPolicy,
    TaxConfiguration,
)


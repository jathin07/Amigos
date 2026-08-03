from app.core.extensions import db
from app.core.base_model import BaseModel


class PackageCategory(db.Model, BaseModel):
    __tablename__ = "package_categories"
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0, nullable=False)


class HotelCategory(db.Model, BaseModel):
    __tablename__ = "hotel_categories"
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0, nullable=False)


class MealPlan(db.Model, BaseModel):
    __tablename__ = "meal_plans"
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0, nullable=False)


class VehicleType(db.Model, BaseModel):
    __tablename__ = "vehicle_types"
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0, nullable=False)


class ActivityType(db.Model, BaseModel):
    __tablename__ = "activity_types"
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0, nullable=False)


class Season(db.Model, BaseModel):
    __tablename__ = "seasons"
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0, nullable=False)


class PaymentMethod(db.Model, BaseModel):
    __tablename__ = "payment_methods_master"
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0, nullable=False)


class Currency(db.Model, BaseModel):
    __tablename__ = "currencies"
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0, nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    is_default = db.Column(db.Boolean, default=False, nullable=False)


class CancellationPolicy(db.Model, BaseModel):
    __tablename__ = "cancellation_policies"
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0, nullable=False)
    refund_percentage = db.Column(db.Numeric(5, 2), nullable=False)
    days_before_travel = db.Column(db.Integer, nullable=False)


class TaxConfiguration(db.Model, BaseModel):
    __tablename__ = "tax_configurations"
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0, nullable=False)
    tax_rate = db.Column(db.Numeric(5, 2), nullable=False)
    tax_type = db.Column(db.String(20), nullable=False)

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import declared_attr
from app.core.extensions import db


class BaseModel:
    """
    Shared BaseModel for all master entities.

    Provides:
    - UUID primary key
    - Audit fields
    - Optimistic locking
    - Soft delete
    """

    @declared_attr
    def id(cls):
        return db.Column(
            db.Uuid(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
        )

    @declared_attr
    def created_at(cls):
        return db.Column(
            db.DateTime(timezone=True),
            nullable=False,
            default=lambda: datetime.now(timezone.utc),
        )

    @declared_attr
    def updated_at(cls):
        return db.Column(
            db.DateTime(timezone=True),
            nullable=False,
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
        )

    @declared_attr
    def created_by(cls):
        return db.Column(
            db.String(36),
            nullable=True,
        )

    @declared_attr
    def updated_by(cls):
        return db.Column(
            db.String(36),
            nullable=True,
        )

    @declared_attr
    def version(cls):
        return db.Column(
            db.Integer,
            nullable=False,
            default=1,
        )

    @declared_attr
    def is_active(cls):
        return db.Column(
            db.Boolean,
            nullable=False,
            default=True,
            index=True,
        )
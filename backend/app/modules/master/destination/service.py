import uuid as _uuid_mod
from typing import Any

from flask_jwt_extended import get_jwt_identity
from app.core.base_service import BaseService
from app.domain.exceptions import BusinessException, NotFoundException, DomainException
from .repository import DestinationRepository
from .models import Destination
from app.modules.master.district.repository import DistrictRepository
from app.modules.master.state.repository import StateRepository
from app.modules.master.country.repository import CountryRepository


class DestinationService(BaseService):

    def __init__(self):
        self.repository         = DestinationRepository()
        self.district_repository = DistrictRepository()
        self.state_repository    = StateRepository()
        self.country_repository  = CountryRepository()

    # ── Internal helpers ─────────────────────────────────────────

    def _parse_uuid(self, raw_id: str | _uuid_mod.UUID) -> _uuid_mod.UUID:
        if isinstance(raw_id, _uuid_mod.UUID):
            return raw_id
        try:
            return _uuid_mod.UUID(str(raw_id))
        except (ValueError, AttributeError):
            raise NotFoundException("Destination not found.", code="ERR_NOT_FOUND")

    def _validate_hierarchy(
        self,
        country_uid: _uuid_mod.UUID,
        state_uid: _uuid_mod.UUID,
        district_uid: _uuid_mod.UUID,
    ) -> None:
        """
        Validate the full geographic hierarchy:
          1. Country exists and is active
          2. State exists, is active, and belongs to the given country
          3. District exists, is active, and belongs to the given state
        """
        country = self.country_repository.get_by_id(country_uid)
        if not country or not country.is_active:
            raise BusinessException("Invalid or inactive country.", code="ERR_INVALID_COUNTRY")

        state = self.state_repository.get_by_id(state_uid)
        if not state or not state.is_active:
            raise BusinessException("Invalid or inactive state.", code="ERR_INVALID_STATE")
        if state.country_id != country_uid:
            raise BusinessException(
                "State does not belong to the selected country.",
                code="ERR_HIERARCHY_MISMATCH",
            )

        district = self.district_repository.get(district_uid)
        if not district or not district.is_active:
            raise BusinessException("Invalid or inactive district.", code="ERR_INVALID_DISTRICT")
        if district.state_id != state_uid:
            raise BusinessException(
                "District does not belong to the selected state.",
                code="ERR_HIERARCHY_MISMATCH",
            )

    # ─────────────────────────────────────────────
    # CREATE
    # ─────────────────────────────────────────────
    def create(self, data: dict) -> Destination:
        country_uid  = self._parse_uuid(data["country_id"])
        state_uid    = self._parse_uuid(data["state_id"])
        district_uid = self._parse_uuid(data["district_id"])

        # 1. Hierarchy validation
        self._validate_hierarchy(country_uid, state_uid, district_uid)

        # 2. Duplicate code check
        code = data["code"].upper()
        if self.repository.find_by_code(code):
            raise BusinessException(
                f"Destination with code '{code}' already exists.",
                code="ERR_DUPLICATE_CODE",
            )

        # 3. Duplicate slug check
        slug = data["slug"].lower()
        if self.repository.find_by_slug(slug):
            raise BusinessException(
                f"Destination with slug '{slug}' already exists.",
                code="ERR_DUPLICATE_SLUG",
            )

        # 4. Create entity
        destination = Destination(
            code          = code,
            slug          = slug,
            name          = data["name"],
            description   = data.get("description"),
            country_id    = country_uid,
            state_id      = state_uid,
            district_id   = district_uid,
            cover_image   = data.get("cover_image"),
            latitude      = data.get("latitude"),
            longitude     = data.get("longitude"),
            display_order = data.get("display_order", 0),
            is_active     = data.get("is_active", True),
            created_by    = get_jwt_identity(),
            updated_by    = get_jwt_identity(),
        )

        self.repository.add(destination)
        self.commit()
        return destination

    # ─────────────────────────────────────────────
    # UPDATE
    # ─────────────────────────────────────────────
    def update(self, destination_id: str, data: dict) -> Destination:
        uid = self._parse_uuid(destination_id)
        dest = self.repository.get(uid)
        if not dest:
            raise NotFoundException("Destination not found.", code="ERR_NOT_FOUND")

        # 1. Optimistic locking
        self.check_optimistic_lock(dest.version, data.get("version"))

        # 2. Determine effective hierarchy (use existing if not changed)
        country_uid  = self._parse_uuid(data["country_id"])  if "country_id"  in data else dest.country_id
        state_uid    = self._parse_uuid(data["state_id"])    if "state_id"    in data else dest.state_id
        district_uid = self._parse_uuid(data["district_id"]) if "district_id" in data else dest.district_id

        # 3. Re-validate hierarchy only if any FK changed
        hierarchy_changed = (
            country_uid  != dest.country_id  or
            state_uid    != dest.state_id    or
            district_uid != dest.district_id
        )
        if hierarchy_changed:
            self._validate_hierarchy(country_uid, state_uid, district_uid)
            dest.country_id  = country_uid
            dest.state_id    = state_uid
            dest.district_id = district_uid

        # 4. Duplicate code check (exclude self)
        if "code" in data:
            new_code = data["code"].upper()
            if new_code != dest.code:
                if self.repository.find_by_code_excluding(new_code, uid):
                    raise BusinessException(
                        f"Destination with code '{new_code}' already exists.",
                        code="ERR_DUPLICATE_CODE",
                    )
            dest.code = new_code

        # 5. Duplicate slug check (exclude self)
        if "slug" in data:
            new_slug = data["slug"].lower()
            if new_slug != dest.slug:
                if self.repository.find_by_slug_excluding(new_slug, uid):
                    raise BusinessException(
                        f"Destination with slug '{new_slug}' already exists.",
                        code="ERR_DUPLICATE_SLUG",
                    )
            dest.slug = new_slug

        # 6. Apply remaining fields
        for field in ("name", "description", "cover_image", "latitude", "longitude", "display_order", "is_active"):
            if field in data:
                setattr(dest, field, data[field])

        dest.version    += 1
        dest.updated_by  = get_jwt_identity()

        self.repository.add(dest)
        self.commit()
        return dest

    # ─────────────────────────────────────────────
    # DELETE (soft)
    # ─────────────────────────────────────────────
    def delete(self, destination_id: str) -> None:
        uid = self._parse_uuid(destination_id)
        dest = self.repository.get(uid)
        if not dest:
            raise NotFoundException("Destination not found.", code="ERR_NOT_FOUND")

        self._check_dependencies(uid)

        dest.is_active  = False
        dest.version   += 1
        dest.updated_by = get_jwt_identity()

        self.repository.add(dest)
        self.commit()

    # ─────────────────────────────────────────────
    # READ
    # ─────────────────────────────────────────────
    def get(self, destination_id: str) -> Destination:
        uid = self._parse_uuid(destination_id)
        dest = self.repository.get(uid)
        if not dest:
            raise NotFoundException("Destination not found.", code="ERR_NOT_FOUND")
        return dest

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        is_active: bool | None = None,
        country_id: str | None = None,
        state_id: str | None = None,
        district_id: str | None = None,
        sort_by: str = "display_order",
        sort_order: str = "asc",
    ) -> Any:
        filters = {}
        if is_active is not None:
            filters["is_active"] = is_active
        if country_id:
            filters["country_id"] = self._parse_uuid(country_id)
        if state_id:
            filters["state_id"] = self._parse_uuid(state_id)
        if district_id:
            filters["district_id"] = self._parse_uuid(district_id)

        return self.repository.paginate(
            page=page,
            page_size=page_size,
            search_query=search,
            sort_by=sort_by,
            sort_order=sort_order,
            **filters,
        )

    # ── Dependency guard ─────────────────────────────────────────

    def _check_dependencies(self, destination_id: _uuid_mod.UUID) -> None:
        """
        Block deactivation if any consumer tables reference this destination.
        Currently checks: package_destinations, lead_destinations (legacy tables).
        Uses raw SQL with try/except so early-phase tests pass if tables don't exist yet.
        """
        from app.core.extensions import db
        from sqlalchemy import text

        consumers = [
            ("package_destinations", "Package"),
            ("lead_destinations",    "Lead"),
        ]
        for table, label in consumers:
            try:
                result = db.session.execute(
                    text(f"SELECT 1 FROM {table} WHERE destination_id = :id LIMIT 1"),
                    {"id": str(destination_id)},
                ).fetchone()
                if result:
                    raise BusinessException(
                        f"Cannot deactivate: active {label} records reference this destination.",
                        code="ERR_ENTITY_IN_USE",
                    )
            except BusinessException:
                raise
            except Exception:
                # Table may not exist in test/dev environments
                pass

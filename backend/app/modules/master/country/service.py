import uuid as _uuid_mod

from flask_jwt_extended import get_jwt_identity
from app.core.base_service import BaseService
from app.domain.exceptions import BusinessException, NotFoundException, DomainException
from .repository import CountryRepository
from .models import Country


class CountryService(BaseService):

    def __init__(self):
        self.repository = CountryRepository()

    # ── internal helper ──────────────────────────────────────────
    def _parse_uuid(self, raw_id: str) -> _uuid_mod.UUID:
        """Convert a string ID from the URL into a UUID object.
        Raises NotFoundException for malformed values so callers get 404."""
        try:
            return _uuid_mod.UUID(str(raw_id))
        except (ValueError, AttributeError):
            raise NotFoundException("Country not found.", code="ERR_NOT_FOUND")

    # ─────────────────────────────────────────────
    # CREATE
    # Step 1: Validate DTO      (done in route via Marshmallow)
    # Step 2: Duplicate Check
    # Step 3: FK Validation     (none for Country — it is the root entity)
    # Step 4: Business Rules    (none beyond duplicate)
    # Step 5: Set Audit Fields
    # Step 6: Persist
    # Step 7: Commit
    # ─────────────────────────────────────────────
    def create(self, data: dict) -> Country:
        code = data["code"]

        if self.repository.find_by_code(code):
            raise BusinessException(
                f"Country with code '{code}' already exists.",
                code="ERR_DUPLICATE_CODE",
            )

        identity = get_jwt_identity()
        country = Country(
            name          = data["name"],
            code          = code,
            phone_code    = data.get("phone_code"),
            description   = data.get("description"),
            display_order = data.get("display_order", 0),
            is_active     = data.get("is_active", True),
            created_by    = identity,
            updated_by    = identity,
        )

        self.repository.add(country)
        self.commit()
        return country

    # ─────────────────────────────────────────────
    # UPDATE
    # Step 1: Entity Exists
    # Step 2: Optimistic Lock
    # Step 3: Validate DTO      (done in route via Marshmallow)
    # Step 4: Duplicate Check (exclude self)
    # Step 5: FK Validation     (none for Country)
    # Step 6: Apply + Audit
    # Step 7: Commit
    # ─────────────────────────────────────────────
    def update(self, country_id: str, data: dict) -> Country:
        uid = self._parse_uuid(country_id)
        country = self.repository.get_by_id(uid)
        if not country:
            raise NotFoundException("Country not found.", code="ERR_NOT_FOUND")

        expected_version = data.pop("version")
        self.check_optimistic_lock(country.version, expected_version)

        new_code = data.get("code")
        if new_code and new_code != country.code:
            if self.repository.find_by_code_excluding(new_code, country.id):
                raise BusinessException(
                    f"Country with code '{new_code}' already exists.",
                    code="ERR_DUPLICATE_CODE",
                )

        for key, value in data.items():
            setattr(country, key, value)

        country.version    += 1
        country.updated_by  = get_jwt_identity()

        self.commit()
        return country

    # ─────────────────────────────────────────────
    # DELETE (Soft)
    # Step 1: Entity Exists
    # Step 2: Dependency Check (active States)
    # Step 3: Soft Delete
    # Step 4: Commit
    # ─────────────────────────────────────────────
    def delete(self, country_id: str) -> None:
        uid = self._parse_uuid(country_id)
        country = self.repository.get_by_id(uid)
        if not country:
            raise NotFoundException("Country not found.", code="ERR_NOT_FOUND")

        self._check_dependencies(uid)

        country.is_active  = False
        country.version   += 1
        country.updated_by = get_jwt_identity()

        self.commit()

    def _check_dependencies(self, country_id: str) -> None:
        """Prevent deactivation if active states reference this country."""
        from sqlalchemy import select, func
        from app.core.extensions import db
        # Lazy import to avoid circular imports when states table may not yet exist
        try:
            from sqlalchemy import text
            result = db.session.execute(
                text("SELECT 1 FROM states WHERE country_id = :id AND is_active = true LIMIT 1"),
                {"id": str(country_id)},
            ).fetchone()
            if result:
                raise BusinessException(
                    "Cannot deactivate: active states are linked to this country.",
                    code="ERR_ENTITY_IN_USE",
                )
        except BusinessException:
            raise
        except Exception:
            # Table may not exist yet during early migration phases — allow delete
            pass

    # ─────────────────────────────────────────────
    # READ
    # ─────────────────────────────────────────────
    def get(self, country_id: str) -> Country:
        uid = self._parse_uuid(country_id)
        country = self.repository.get_by_id(uid)
        if not country:
            raise NotFoundException("Country not found.", code="ERR_NOT_FOUND")
        return country

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str = None,
        is_active: bool = None,
        sort_by: str = "display_order",
        sort_order: str = "asc",
    ):
        filters = {}
        if is_active is not None:
            filters["is_active"] = is_active

        return self.repository.paginate(
            page=page,
            page_size=page_size,
            search_query=search,
            sort_by=sort_by,
            sort_order=sort_order,
            **filters,
        )

    def lookup(self):
        """Lightweight list for dropdowns — active countries only."""
        return self.repository.list_active()

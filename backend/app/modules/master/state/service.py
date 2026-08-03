import uuid as _uuid_mod
from typing import Any

from flask_jwt_extended import get_jwt_identity
from app.core.base_service import BaseService
from app.domain.exceptions import BusinessException, NotFoundException, DomainException
from .repository import StateRepository
from .models import State
from app.modules.master.country.repository import CountryRepository


class StateService(BaseService):

    def __init__(self):
        self.repository = StateRepository()
        self.country_repository = CountryRepository()

    # ── internal helper ──────────────────────────────────────────
    def _parse_uuid(self, raw_id: str | _uuid_mod.UUID) -> _uuid_mod.UUID:
        """Convert a string ID into a UUID object."""
        if isinstance(raw_id, _uuid_mod.UUID):
            return raw_id
        try:
            return _uuid_mod.UUID(str(raw_id))
        except (ValueError, AttributeError):
            raise NotFoundException("State not found.", code="ERR_NOT_FOUND")

    # ─────────────────────────────────────────────
    # CREATE
    # ─────────────────────────────────────────────
    def create(self, data: dict) -> State:
        country_uid = self._parse_uuid(data["country_id"])
        
        # 1. FK Validation (Country Exists & is Active)
        country = self.country_repository.get_by_id(country_uid)
        if not country or not country.is_active:
            raise BusinessException("Invalid or inactive country selected.", code="ERR_INVALID_COUNTRY")

        # 2. Duplicate Validation (Code within same country)
        code = data.get("code").upper()
        if self.repository.find_by_code(code, country_uid):
            raise BusinessException(
                f"State with code '{code}' already exists in this country.",
                code="ERR_DUPLICATE_CODE"
            )

        # 3. Create Entity
        state = State(
            name=data["name"],
            code=code,
            country_id=country_uid,
            description=data.get("description"),
            display_order=data.get("display_order", 0),
            is_active=data.get("is_active", True),
            created_by=get_jwt_identity(),
            updated_by=get_jwt_identity()
        )

        # 4. Commit
        self.repository.add(state)
        self.commit()
        return state

    # ─────────────────────────────────────────────
    # UPDATE
    # ─────────────────────────────────────────────
    def update(self, state_id: str, data: dict) -> State:
        uid = self._parse_uuid(state_id)
        state = self.repository.get_by_id(uid)
        if not state:
            raise NotFoundException("State not found.", code="ERR_NOT_FOUND")

        # 1. Optimistic Locking
        self.check_optimistic_lock(state.version, data.get("version"))

        # 2. FK Validation if country_id changed
        country_uid = state.country_id
        if "country_id" in data and data["country_id"] != state.country_id:
            country_uid = self._parse_uuid(data["country_id"])
            country = self.country_repository.get_by_id(country_uid)
            if not country or not country.is_active:
                raise BusinessException("Invalid or inactive country selected.", code="ERR_INVALID_COUNTRY")
            state.country_id = country_uid

        # 3. Duplicate Validation if code or country changed
        if "code" in data:
            new_code = data["code"].upper()
            if new_code != state.code or country_uid != state.country_id:
                existing = self.repository.find_by_code(new_code, country_uid)
                if existing and existing.id != state.id:
                    raise BusinessException(
                        f"State with code '{new_code}' already exists in this country.",
                        code="ERR_DUPLICATE_CODE"
                    )
            state.code = new_code

        # 4. Update fields
        if "name" in data:
            state.name = data["name"]
        if "description" in data:
            state.description = data["description"]
        if "display_order" in data:
            state.display_order = data["display_order"]
        if "is_active" in data:
            state.is_active = data["is_active"]

        state.version += 1
        state.updated_by = get_jwt_identity()

        # 5. Commit
        self.repository.add(state)
        self.commit()
        return state

    # ─────────────────────────────────────────────
    # DELETE
    # ─────────────────────────────────────────────
    def delete(self, state_id: str) -> None:
        uid = self._parse_uuid(state_id)
        state = self.repository.get_by_id(uid)
        if not state:
            raise NotFoundException("State not found.", code="ERR_NOT_FOUND")

        self._check_dependencies(uid)

        state.is_active = False
        state.version += 1
        state.updated_by = get_jwt_identity()

        self.repository.add(state)
        self.commit()

    # ─────────────────────────────────────────────
    # READ
    # ─────────────────────────────────────────────
    def get(self, state_id: str) -> State:
        uid = self._parse_uuid(state_id)
        state = self.repository.get_by_id(uid)
        if not state:
            raise NotFoundException("State not found.", code="ERR_NOT_FOUND")
        return state

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        is_active: bool | None = None,
        country_id: str | None = None,
        sort_by: str = "display_order",
        sort_order: str = "asc"
    ) -> Any:
        country_uid = None
        if country_id:
            country_uid = self._parse_uuid(country_id)

        filters = {"is_active": is_active if is_active is not None else True}
        if country_uid is not None:
            filters["country_id"] = country_uid

        return self.repository.paginate(
            page=page,
            page_size=page_size,
            search_query=search,
            sort_by=sort_by,
            sort_order=sort_order,
            **filters,
        )

    def lookup(self, country_id: str | None = None):
        """Lightweight list for dropdowns — active states only."""
        if country_id:
            return self.repository.list_by_country(self._parse_uuid(country_id))
        return self.repository.list(is_active=True)

    # ─────────────────────────────────────────────
    # PRIVATE HELPER
    # ─────────────────────────────────────────────
    def _check_dependencies(self, state_id: _uuid_mod.UUID) -> None:
        """Prevent deactivation if active districts reference this state."""
        from app.core.extensions import db
        from sqlalchemy import select, func
        try:
            from app.modules.master.district.models import District
            count = db.session.scalar(
                select(func.count()).select_from(District).where(
                    District.state_id == state_id,
                    District.is_active.is_(True),
                )
            )
            if count and count > 0:
                raise BusinessException(
                    "Cannot deactivate: active districts are linked to this state.",
                    code="ERR_ENTITY_IN_USE",
                )
        except BusinessException:
            raise
        except Exception:
            # Districts module may not be available in all deployment contexts
            pass

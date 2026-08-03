import uuid as _uuid_mod
from typing import Any

from flask_jwt_extended import get_jwt_identity
from app.core.base_service import BaseService
from app.domain.exceptions import BusinessException, NotFoundException, DomainException
from .repository import DistrictRepository
from .models import District
from app.modules.master.state.repository import StateRepository

class DistrictService(BaseService):
    def __init__(self):
        self.repository = DistrictRepository()
        self.state_repository = StateRepository()

    def _parse_uuid(self, raw_id: str | _uuid_mod.UUID) -> _uuid_mod.UUID:
        if isinstance(raw_id, _uuid_mod.UUID):
            return raw_id
        try:
            return _uuid_mod.UUID(str(raw_id))
        except (ValueError, AttributeError):
            raise NotFoundException("District not found.", code="ERR_NOT_FOUND")

    def create(self, data: dict) -> District:
        state_uid = self._parse_uuid(data["state_id"])
        
        state = self.state_repository.get_by_id(state_uid)
        if not state or not state.is_active:
            raise BusinessException("Invalid or inactive state selected.", code="ERR_INVALID_STATE")

        code = data.get("code").upper()
        if self.repository.find_by_code(code, state_uid):
            raise BusinessException(
                f"District with code '{code}' already exists in this state.",
                code="ERR_DUPLICATE_CODE"
            )

        district = District(
            name=data["name"],
            code=code,
            state_id=state_uid,
            description=data.get("description"),
            display_order=data.get("display_order", 0),
            is_active=data.get("is_active", True),
            created_by=get_jwt_identity(),
            updated_by=get_jwt_identity()
        )

        self.repository.add(district)
        self.commit()
        return district

    def update(self, district_id: str, data: dict) -> District:
        uid = self._parse_uuid(district_id)
        district = self.repository.get(uid)
        if not district:
            raise NotFoundException("District not found.", code="ERR_NOT_FOUND")

        self.check_optimistic_lock(district.version, data.get("version"))

        state_uid = district.state_id
        if "state_id" in data:
            new_state_uid = self._parse_uuid(data["state_id"])
            if new_state_uid != district.state_id:  # compare UUID objects, not str vs UUID
                state = self.state_repository.get_by_id(new_state_uid)
                if not state or not state.is_active:
                    raise BusinessException("Invalid or inactive state selected.", code="ERR_INVALID_STATE")
                district.state_id = new_state_uid
                state_uid = new_state_uid

        if "code" in data:
            new_code = data["code"].upper()
            if new_code != district.code or state_uid != district.state_id:
                existing = self.repository.find_by_code(new_code, state_uid)
                if existing and existing.id != district.id:
                    raise BusinessException(
                        f"District with code '{new_code}' already exists in this state.",
                        code="ERR_DUPLICATE_CODE"
                    )
            district.code = new_code

        if "name" in data:
            district.name = data["name"]
        if "description" in data:
            district.description = data["description"]
        if "display_order" in data:
            district.display_order = data["display_order"]
        if "is_active" in data:
            district.is_active = data["is_active"]

        district.version += 1
        district.updated_by = get_jwt_identity()

        self.repository.add(district)
        self.commit()
        return district

    def delete(self, district_id: str) -> None:
        uid = self._parse_uuid(district_id)
        district = self.repository.get(uid)
        if not district:
            raise NotFoundException("District not found.", code="ERR_NOT_FOUND")

        self._check_dependencies(uid)

        district.is_active = False
        district.version += 1
        district.updated_by = get_jwt_identity()

        self.repository.add(district)
        self.commit()

    def get(self, district_id: str) -> District:
        uid = self._parse_uuid(district_id)
        district = self.repository.get(uid)
        if not district:
            raise NotFoundException("District not found.", code="ERR_NOT_FOUND")
        return district

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        is_active: bool | None = None,
        state_id: str | None = None,
        sort_by: str = "display_order",
        sort_order: str = "asc"
    ) -> Any:
        state_uid = None
        if state_id:
            state_uid = self._parse_uuid(state_id)

        filters = {}
        if is_active is not None:
            filters["is_active"] = is_active
        if state_uid is not None:
            filters["state_id"] = state_uid

        return self.repository.paginate(
            page=page,
            page_size=page_size,
            search_query=search,
            sort_by=sort_by,
            sort_order=sort_order,
            **filters,
        )

    def _check_dependencies(self, district_id: _uuid_mod.UUID) -> None:
        """Prevent deactivation if active destinations reference this district."""
        from app.core.extensions import db
        from sqlalchemy import select, func
        try:
            from app.modules.master.destination.models import Destination
            count = db.session.scalar(
                select(func.count()).select_from(Destination).where(
                    Destination.district_id == district_id,
                    Destination.is_active.is_(True),
                )
            )
            if count and count > 0:
                raise BusinessException(
                    "Cannot deactivate: active destinations are linked to this district.",
                    code="ERR_ENTITY_IN_USE",
                )
        except BusinessException:
            raise
        except Exception:
            # Destination module may not be available yet — allow delete
            pass

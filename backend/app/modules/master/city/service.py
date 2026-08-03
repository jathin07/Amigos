import uuid as _uuid_mod
from typing import Any

from flask_jwt_extended import get_jwt_identity
from app.core.base_service import BaseService
from app.domain.exceptions import BusinessException, NotFoundException, DomainException
from .repository import CityRepository
from .models import City
from app.modules.master.state.repository import StateRepository
from app.modules.master.district.repository import DistrictRepository

class CityService(BaseService):
    def __init__(self):
        self.repository = CityRepository()
        self.state_repository = StateRepository()
        self.district_repository = DistrictRepository()

    def _parse_uuid(self, raw_id: str | _uuid_mod.UUID) -> _uuid_mod.UUID:
        if isinstance(raw_id, _uuid_mod.UUID):
            return raw_id
        try:
            return _uuid_mod.UUID(str(raw_id))
        except (ValueError, AttributeError):
            raise NotFoundException("City not found.", code="ERR_NOT_FOUND")

    def create(self, data: dict) -> City:
        state_uid = self._parse_uuid(data["state_id"])
        district_uid = self._parse_uuid(data["District_id"])
        
        state = self.state_repository.get_by_id(state_uid)
        if not state or not state.is_active:
            raise BusinessException("Invalid or inactive state selected.", code="ERR_INVALID_STATE")

        elif not self.district_repository.get(district_uid):
            raise BusinessException("Invalid district selected.", code="ERR_INVALID_DISTRICT")

        code = data.get("code").upper()
        if self.repository.find_by_code(code, state_uid):
            raise BusinessException(
                f"City with code '{code}' already exists in this state.",
                code="ERR_DUPLICATE_CODE"
            )

        city = City(
            name=data["name"],
            code=code,
            district_id=district_uid,
            state_id=state_uid,
            description=data.get("description"),
            display_order=data.get("display_order", 0),
            is_active=data.get("is_active", True),
            created_by=get_jwt_identity(),
            updated_by=get_jwt_identity()
        )

        self.repository.add(city)
        self.commit()
        return city

    def update(self, city_id: str, data: dict) -> City:
        uid = self._parse_uuid(city_id)
        city = self.repository.get(uid)
        if not city:
            raise NotFoundException("City not found.", code="ERR_NOT_FOUND")

        self.check_optimistic_lock(city.version, data.get("version"))

        state_uid = city.state_id
        district_uid = city.district_id
        if "state_id" in data and data["state_id"] != str(city.state_id):
            state_uid = self._parse_uuid(data["state_id"])
            state = self.state_repository.get_by_id(state_uid)
            if not state or not state.is_active:
                raise BusinessException("Invalid or inactive state selected.", code="ERR_INVALID_STATE")
            city.state_id = state_uid

        if "District_id" in data and data["District_id"] != str(city.district_id):
            district_uid = self._parse_uuid(data["District_id"])
            district = self.district_repository.get(district_uid)
            if not district:
                raise BusinessException("Invalid district selected.", code="ERR_INVALID_DISTRICT")
            city.district_id = district_uid

        if "code" in data:
            new_code = data["code"].upper()
            if new_code != city.code or state_uid != city.state_id:
                existing = self.repository.find_by_code(new_code, state_uid)
                if existing and existing.id != city.id:
                    raise BusinessException(
                        f"City with code '{new_code}' already exists in this state.",
                        code="ERR_DUPLICATE_CODE"
                    )
            city.code = new_code

        if "name" in data:
            city.name = data["name"]
        if "description" in data:
            city.description = data["description"]
        if "display_order" in data:
            city.display_order = data["display_order"]
        if "is_active" in data:
            city.is_active = data["is_active"]

        city.version += 1
        city.updated_by = get_jwt_identity()

        self.repository.add(city)
        self.commit()
        return city

    def delete(self, city_id: str) -> None:
        uid = self._parse_uuid(city_id)
        city = self.repository.get(uid)
        if not city:
            raise NotFoundException("City not found.", code="ERR_NOT_FOUND")

        self._check_dependencies(uid)

        city.is_active = False
        city.version += 1
        city.updated_by = get_jwt_identity()

        self.repository.add(city)
        self.commit()

    def get(self, city_id: str) -> City:
        uid = self._parse_uuid(city_id)
        city = self.repository.get(uid)
        if not city:
            raise NotFoundException("City not found.", code="ERR_NOT_FOUND")
        return city

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        is_active: bool | None = None,
        state_id: str | None = None,
        district_id: str | None = None,
        sort_by: str = "display_order",
        sort_order: str = "asc"
    ) -> Any:
        if state_id:
            state_uid = self._parse_uuid(state_id)
        elif district_id:
            district_uid = self._parse_uuid(district_id)
        
        return self.repository.paginate(
            page=page,
            page_size=page_size,
            search_query=search,
            sort_by=sort_by,
            sort_order=sort_order,
            **{k: v for k, v in [("is_active", is_active), ("state_id", state_uid if state_id else None), ("district_id", district_uid if district_id else None)] if v is not None}
            
        )

    def _check_dependencies(self, city_id: _uuid_mod.UUID) -> None:
        """Check if City has any active dependencies (Destinations)."""
        pass

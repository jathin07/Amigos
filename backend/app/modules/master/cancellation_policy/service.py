import uuid as _uuid_mod
from typing import Any
from flask_jwt_extended import get_jwt_identity
from app.core.base_service import BaseService
from app.domain.exceptions import BusinessException, NotFoundException
from .repository import CancellationPolicyRepository
from .models import CancellationPolicy

class CancellationPolicyService(BaseService):
    def __init__(self):
        self.repository = CancellationPolicyRepository()

    def _parse_uuid(self, raw_id):
        if isinstance(raw_id, _uuid_mod.UUID): return raw_id
        try: return _uuid_mod.UUID(str(raw_id))
        except (ValueError, AttributeError): raise NotFoundException("Cancellation policy not found.", code="ERR_NOT_FOUND")

    def create(self, data: dict) -> CancellationPolicy:
        code = data["code"].upper()
        if self.repository.find_by_code(code):
            raise BusinessException(f"Code '{code}' already exists.", code="ERR_DUPLICATE_CODE")
            
        entity = CancellationPolicy(
            code=code, name=data["name"], description=data.get("description"),
            display_order=data.get("display_order", 0), is_active=data.get("is_active", True),
            refund_percentage=data["refund_percentage"], days_before_travel=data["days_before_travel"],
            policy_type=data.get("policy_type", "PERCENTAGE"),
            created_by=get_jwt_identity(), updated_by=get_jwt_identity(),
        )
        self.repository.add(entity)
        self.commit()
        return entity

    def update(self, entity_id: str, data: dict) -> CancellationPolicy:
        uid = self._parse_uuid(entity_id)
        entity = self.repository.get(uid)
        if not entity: raise NotFoundException("Cancellation policy not found.", code="ERR_NOT_FOUND")
        self.check_optimistic_lock(entity.version, data.get("version"))
        
        if "code" in data:
            new_code = data["code"].upper()
            if new_code != entity.code and self.repository.find_by_code_excluding(new_code, uid):
                raise BusinessException(f"Code '{new_code}' already exists.", code="ERR_DUPLICATE_CODE")
            entity.code = new_code
            
        for field in ("name", "description", "display_order", "is_active", "refund_percentage", "days_before_travel", "policy_type"):
            if field in data: setattr(entity, field, data[field])
            
        entity.version += 1
        entity.updated_by = get_jwt_identity()
        self.repository.add(entity)
        self.commit()
        return entity

    def delete(self, entity_id: str) -> None:
        uid = self._parse_uuid(entity_id)
        entity = self.repository.get(uid)
        if not entity: raise NotFoundException("Cancellation policy not found.", code="ERR_NOT_FOUND")
        entity.is_active = False
        entity.version += 1
        entity.updated_by = get_jwt_identity()
        self.repository.add(entity)
        self.commit()

    def get(self, entity_id: str) -> CancellationPolicy:
        uid = self._parse_uuid(entity_id)
        entity = self.repository.get(uid)
        if not entity: raise NotFoundException("Cancellation policy not found.", code="ERR_NOT_FOUND")
        return entity

    def list(self, page=1, page_size=20, search=None, is_active=None, sort_by="display_order", sort_order="asc") -> Any:
        filters = {}
        if is_active is not None: filters["is_active"] = is_active
        return self.repository.paginate(page=page, page_size=page_size, search_query=search, sort_by=sort_by, sort_order=sort_order, **filters)

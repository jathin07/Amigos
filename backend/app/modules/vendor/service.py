import uuid
from datetime import datetime, timezone
from flask_jwt_extended import get_jwt_identity
from app.core.base_service import BaseService
from app.domain.exceptions import BusinessException, NotFoundException, DomainException
from app.models import Vendor, VendorType, UserAccount
from .repository import VendorRepository


class VendorService(BaseService):
    def __init__(self):
        self.repository = VendorRepository()

    def _resolve_team_member_id(self) -> uuid.UUID | None:
        """Resolve current authenticated user's TeamMember ID."""
        user_id_str = get_jwt_identity()
        if user_id_str:
            try:
                user_id = uuid.UUID(str(user_id_str))
                user_acc = UserAccount.query.get(user_id)
                if user_acc:
                    return user_acc.team_member_id
            except (ValueError, AttributeError):
                pass
        return None

    def _validate_vendor_type(self, vendor_type_id: uuid.UUID) -> None:
        vt = VendorType.query.get(vendor_type_id)
        if not vt or not vt.is_active:
            raise BusinessException(
                "Invalid or inactive Vendor Type.",
                code="ERR_INVALID_VENDOR_TYPE"
            )

    def get(self, vendor_id: str) -> Vendor:
        try:
            uid = uuid.UUID(str(vendor_id))
        except ValueError:
            raise NotFoundException("Vendor not found", code="ERR_VENDOR_NOT_FOUND")

        vendor = self.repository.get(uid)
        if not vendor or vendor.is_deleted:
            raise NotFoundException("Vendor not found", code="ERR_VENDOR_NOT_FOUND")
        return vendor

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        sort_by: str | None = "vendor_name",
        sort_order: str = "asc",
        **filters,
    ):
        filters["is_deleted"] = False
        return self.repository.paginate(
            page=page,
            page_size=page_size,
            search_query=search,
            sort_by=sort_by,
            sort_order=sort_order,
            **filters,
        )

    def create(self, data: dict) -> Vendor:
        # Validate Vendor Type
        self._validate_vendor_type(data["vendor_type_id"])

        # Check duplicate GST number
        gst = data.get("gst_number")
        if gst:
            norm_gst = gst.strip().upper()
            if self.repository.find_by_gst_number(norm_gst):
                raise BusinessException(
                    "Vendor with this GST number already exists",
                    code="ERR_VENDOR_DUPLICATE_GST"
                )

        team_member_id = self._resolve_team_member_id()

        vendor = Vendor(
            vendor_name=data["vendor_name"].strip(),
            vendor_type_id=data["vendor_type_id"],
            contact_person=data.get("contact_person"),
            phone=data["phone"].strip(),
            email=data.get("email"),
            address=data.get("address"),
            city=data.get("city"),
            state=data.get("state"),
            service_area=data.get("service_area"),
            internal_rating=data.get("internal_rating"),
            bank_account_name=data.get("bank_account_name"),
            bank_account_number=data.get("bank_account_number"),
            ifsc=data.get("ifsc"),
            gst_number=gst.strip().upper() if gst else None,
            notes=data.get("notes"),
            is_active=data.get("is_active", True),
            is_verified=False,
            verified_at=None,
            version=1
        )

        if team_member_id:
            vendor.created_by_team_member_id = team_member_id
            vendor.updated_by_team_member_id = team_member_id

        self.repository.add(vendor)
        self.commit()
        return vendor

    def update(self, vendor_id: str, data: dict) -> Vendor:
        uid = uuid.UUID(str(vendor_id))
        vendor = self.repository.get(uid)
        if not vendor or vendor.is_deleted:
            raise NotFoundException("Vendor not found", code="ERR_VENDOR_NOT_FOUND")

        # Optimistic locking check
        self.check_optimistic_lock(vendor.version, data.get("version"))

        # Validate Vendor Type if provided
        if "vendor_type_id" in data:
            self._validate_vendor_type(data["vendor_type_id"])

        # Check duplicate GST number if provided
        if "gst_number" in data:
            gst = data["gst_number"]
            if gst:
                norm_gst = gst.strip().upper()
                if self.repository.find_by_gst_number_excluding(norm_gst, uid):
                    raise BusinessException(
                        "Vendor with this GST number already exists",
                        code="ERR_VENDOR_DUPLICATE_GST"
                    )

        # Apply mutable updates
        for field in (
            "vendor_name", "vendor_type_id", "contact_person", "phone", "email",
            "address", "city", "state", "service_area", "internal_rating",
            "bank_account_name", "bank_account_number", "ifsc", "gst_number",
            "notes", "is_active"
        ):
            if field in data:
                val = data[field]
                if isinstance(val, str) and field in ("vendor_name", "phone", "gst_number"):
                    val = val.strip()
                    if field == "gst_number":
                        val = val.upper()
                setattr(vendor, field, val)

        team_member_id = self._resolve_team_member_id()
        if team_member_id:
            vendor.updated_by_team_member_id = team_member_id

        vendor.version += 1

        self.repository.add(vendor)
        self.commit()
        return vendor

    def delete(self, vendor_id: str) -> None:
        uid = uuid.UUID(str(vendor_id))
        vendor = self.repository.get(uid)
        if not vendor or vendor.is_deleted:
            raise NotFoundException("Vendor not found", code="ERR_VENDOR_NOT_FOUND")

        # Soft delete is setting is_active = False, is_deleted = True
        vendor.is_active = False
        vendor.is_deleted = True
        vendor.deleted_at = datetime.now(timezone.utc)

        team_member_id = self._resolve_team_member_id()
        if team_member_id:
            vendor.deleted_by_team_member_id = team_member_id
            vendor.updated_by_team_member_id = team_member_id

        vendor.version += 1

        self.repository.add(vendor)
        self.commit()

    def verify(self, vendor_id: str) -> Vendor:
        uid = uuid.UUID(str(vendor_id))
        vendor = self.repository.get(uid)
        if not vendor or vendor.is_deleted:
            raise NotFoundException("Vendor not found", code="ERR_VENDOR_NOT_FOUND")

        vendor.is_verified = True
        vendor.verified_at = datetime.now(timezone.utc)

        team_member_id = self._resolve_team_member_id()
        if team_member_id:
            vendor.updated_by_team_member_id = team_member_id

        vendor.version += 1

        self.repository.add(vendor)
        self.commit()
        return vendor

    def unverify(self, vendor_id: str) -> Vendor:
        uid = uuid.UUID(str(vendor_id))
        vendor = self.repository.get(uid)
        if not vendor or vendor.is_deleted:
            raise NotFoundException("Vendor not found", code="ERR_VENDOR_NOT_FOUND")

        vendor.is_verified = False
        vendor.verified_at = None

        team_member_id = self._resolve_team_member_id()
        if team_member_id:
            vendor.updated_by_team_member_id = team_member_id

        vendor.version += 1

        self.repository.add(vendor)
        self.commit()
        return vendor

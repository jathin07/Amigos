import uuid
from datetime import datetime, timezone
from flask_jwt_extended import get_jwt_identity
from app.core.base_service import BaseService
from app.domain.exceptions import BusinessException, NotFoundException, DomainException
from app.models import TeamMember, Role, Department, UserAccount
from .repository import TeamRepository


class TeamService(BaseService):
    def __init__(self):
        self.repository = TeamRepository()

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

    def _validate_lookups(self, data: dict, exclude_id: uuid.UUID | None = None) -> None:
        # Validate department
        dept_id = data.get("department_id")
        if dept_id:
            dept = Department.query.get(dept_id)
            if not dept or not dept.is_active:
                raise BusinessException("Invalid or inactive department.", code="ERR_INVALID_DEPARTMENT")

        # Validate role
        role_id = data.get("role_id")
        if role_id:
            r = Role.query.get(role_id)
            if not r or not r.is_active:
                raise BusinessException("Invalid or inactive role.", code="ERR_INVALID_ROLE")

        # Validate reporting manager
        mgr_id = data.get("reporting_manager_id")
        if mgr_id:
            if exclude_id and mgr_id == exclude_id:
                raise BusinessException("A team member cannot be their own reporting manager.", code="ERR_INVALID_MANAGER")
            mgr = self.repository.get(mgr_id)
            if not mgr or not mgr.is_active or mgr.is_deleted:
                raise BusinessException("Invalid or inactive reporting manager.", code="ERR_INVALID_MANAGER")

    def _validate_employment_dates(self, joined_date, left_date) -> None:
        if joined_date and left_date and left_date < joined_date:
            raise BusinessException(
                "Left date must be greater than or equal to joined date.",
                code="ERR_VALIDATION"
            )

    def get(self, member_id: str) -> TeamMember:
        try:
            uid = uuid.UUID(str(member_id))
        except ValueError:
            raise NotFoundException("Team member not found.", code="ERR_NOT_FOUND")

        member = self.repository.get(uid)
        if not member or member.is_deleted:
            raise NotFoundException("Team member not found.", code="ERR_NOT_FOUND")
        return member

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        sort_by: str | None = "created_at",
        sort_order: str = "desc",
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

    def create(self, data: dict) -> TeamMember:
        # Check duplicate employee code
        code = data["employee_code"].strip()
        if self.repository.find_by_employee_code(code):
            raise BusinessException(
                f"Team member with employee code '{code}' already exists.",
                code="ERR_DUPLICATE_EMPLOYEE_CODE"
            )

        # Check duplicate official email
        email = data["official_email"].strip()
        if self.repository.find_by_official_email(email):
            raise BusinessException(
                f"Team member with official email '{email}' already exists.",
                code="ERR_DUPLICATE_EMAIL"
            )

        self._validate_lookups(data)
        self._validate_employment_dates(data.get("joined_date"), data.get("left_date"))

        team_member_id = self._resolve_team_member_id()

        member = TeamMember(
            first_name=data["first_name"],
            last_name=data.get("last_name"),
            display_name=data["display_name"],
            avatar_url=data.get("avatar_url"),
            dob=data.get("dob"),
            gender=data.get("gender"),
            employee_code=code,
            official_email=email,
            personal_email=data.get("personal_email"),
            phone=data["phone"],
            designation=data.get("designation"),
            department_id=data.get("department_id"),
            role_id=data.get("role_id"),
            reporting_manager_id=data.get("reporting_manager_id"),
            employment_status=data.get("employment_status"),
            joined_date=data.get("joined_date"),
            left_date=data.get("left_date"),
            is_active=data.get("is_active", True),
            emergency_contact_name=data.get("emergency_contact_name"),
            emergency_contact_phone=data.get("emergency_contact_phone"),
            version=1
        )

        if team_member_id:
            member.created_by_team_member_id = team_member_id
            member.updated_by_team_member_id = team_member_id

        self.repository.add(member)
        self.commit()
        return member

    def update(self, member_id: str, data: dict) -> TeamMember:
        uid = uuid.UUID(str(member_id))
        member = self.repository.get(uid)
        if not member or member.is_deleted:
            raise NotFoundException("Team member not found.", code="ERR_NOT_FOUND")

        # 1. Optimistic locking check
        self.check_optimistic_lock(member.version, data.get("version"))

        # 2. Check duplicate employee code (excluding self)
        if "employee_code" in data:
            code = data["employee_code"].strip()
            if self.repository.find_by_employee_code_excluding(code, uid):
                raise BusinessException(
                    f"Team member with employee code '{code}' already exists.",
                    code="ERR_DUPLICATE_EMPLOYEE_CODE"
                )
            member.employee_code = code

        # 3. Check duplicate official email (excluding self)
        if "official_email" in data:
            email = data["official_email"].strip()
            if self.repository.find_by_official_email_excluding(email, uid):
                raise BusinessException(
                    f"Team member with official email '{email}' already exists.",
                    code="ERR_DUPLICATE_EMAIL"
                )
            member.official_email = email

        # 4. Lookup and hierarchy validations
        self._validate_lookups(data, exclude_id=uid)

        # 5. Employment dates validation
        joined_date = data.get("joined_date") if "joined_date" in data else member.joined_date
        left_date = data.get("left_date") if "left_date" in data else member.left_date
        self._validate_employment_dates(joined_date, left_date)

        # 6. Apply updates
        for field in (
            "first_name", "last_name", "display_name", "avatar_url", "dob", "gender",
            "personal_email", "phone", "designation", "department_id", "role_id",
            "reporting_manager_id", "employment_status", "joined_date", "left_date",
            "is_active", "emergency_contact_name", "emergency_contact_phone"
        ):
            if field in data:
                setattr(member, field, data[field])

        # 7. Auditing & lock increment
        team_member_id = self._resolve_team_member_id()
        if team_member_id:
            member.updated_by_team_member_id = team_member_id

        member.version += 1

        self.repository.add(member)
        self.commit()
        return member

    def delete(self, member_id: str) -> None:
        uid = uuid.UUID(str(member_id))
        member = self.repository.get(uid)
        if not member or member.is_deleted:
            raise NotFoundException("Team member not found.", code="ERR_NOT_FOUND")

        # Soft delete is setting is_active = False, is_deleted = True
        member.is_active = False
        member.is_deleted = True
        member.deleted_at = datetime.now(timezone.utc)

        team_member_id = self._resolve_team_member_id()
        if team_member_id:
            member.deleted_by_team_member_id = team_member_id
            member.updated_by_team_member_id = team_member_id

        member.version += 1

        self.repository.add(member)
        self.commit()

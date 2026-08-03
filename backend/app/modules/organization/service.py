import uuid
from flask_jwt_extended import get_jwt_identity
from app.core.base_service import BaseService
from app.domain.exceptions import BusinessException, NotFoundException
from app.models import Organization, OrganizationType, UserAccount
from .repository import OrganizationRepository


class OrganizationService(BaseService):
    def __init__(self):
        self.repository = OrganizationRepository()

    def get_active(self) -> Organization:
        """Fetch the single active organization."""
        org = self.repository.get_active()
        if not org:
            raise NotFoundException("Organization configuration not found.", code="ERR_NOT_FOUND")
        return org

    def update_active(self, data: dict) -> Organization:
        """Create or update the single active organization configuration."""
        # Find logged in TeamMember ID from UserAccount ID stored in JWT
        team_member_id = None
        user_id_str = get_jwt_identity()
        if user_id_str:
            try:
                user_id = uuid.UUID(str(user_id_str))
                user_acc = UserAccount.query.get(user_id)
                if user_acc:
                    team_member_id = user_acc.team_member_id
            except (ValueError, AttributeError):
                pass

        org = self.repository.get_active()

        if not org:
            # Creation mode (no active organization exists)
            if "organization_name" not in data or "organization_type_id" not in data:
                raise BusinessException(
                    "Organization name and organization type ID are required to initialize organization.",
                    code="ERR_VALIDATION"
                )

            # Validate organization type FK
            org_type_id = data["organization_type_id"]
            if isinstance(org_type_id, str):
                try:
                    org_type_id = uuid.UUID(org_type_id)
                except ValueError:
                    raise BusinessException("Invalid organization type ID format.", code="ERR_VALIDATION")

            org_type = OrganizationType.query.get(org_type_id)
            if not org_type:
                raise BusinessException(
                    f"OrganizationType with ID {org_type_id} does not exist.",
                    code="ERR_INVALID_TYPE"
                )

            org = Organization(
                organization_name=data["organization_name"],
                organization_type_id=org_type_id,
                address=data.get("address"),
                city=data.get("city"),
                state=data.get("state"),
                phone=data.get("phone"),
                email=data.get("email"),
                website=data.get("website"),
                notes=data.get("notes"),
                is_active=data.get("is_active", True)
            )
            if team_member_id:
                org.created_by_team_member_id = team_member_id
                org.updated_by_team_member_id = team_member_id

            self.repository.add(org)
            # Flush to get the organization ID generated for children FKs
            db = self.repository.model_class.metadata
            from app.core.extensions import db as db_ext
            db_ext.session.flush()
        else:
            # Update mode
            if "organization_type_id" in data:
                org_type_id = data["organization_type_id"]
                if isinstance(org_type_id, str):
                    try:
                        org_type_id = uuid.UUID(org_type_id)
                    except ValueError:
                        raise BusinessException("Invalid organization type ID format.", code="ERR_VALIDATION")

                org_type = OrganizationType.query.get(org_type_id)
                if not org_type:
                    raise BusinessException(
                        f"OrganizationType with ID {org_type_id} does not exist.",
                        code="ERR_INVALID_TYPE"
                    )
                org.organization_type_id = org_type_id

            if "organization_name" in data:
                org.organization_name = data["organization_name"]

            for field in ("address", "city", "state", "phone", "email", "website", "notes", "is_active"):
                if field in data:
                    setattr(org, field, data[field])

            if team_member_id:
                org.updated_by_team_member_id = team_member_id

            self.repository.add(org)

        # Sync nested divisions
        if "divisions" in data and data["divisions"] is not None:
            self.repository.sync_divisions(org, data["divisions"], team_member_id)

        # Sync nested contact persons
        if "contact_persons" in data and data["contact_persons"] is not None:
            self.repository.sync_contact_persons(org, data["contact_persons"], team_member_id)

        self.commit()
        return org

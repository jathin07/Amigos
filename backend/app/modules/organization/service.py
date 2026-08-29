import uuid
from app.core.base_service import BaseService
from app.domain.exceptions import NotFoundException, BusinessException
from app.models import Organization, OrganizationType, UserAccount
from .repository import OrganizationRepository
from app.core.extensions import db
from flask_jwt_extended import get_jwt_identity

class OrganizationService(BaseService):
  def __init__(self):
    self.repository = OrganizationRepository()

  def _get_team_member_id(self) -> uuid.UUID | None:
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

  def list_organizations(self, page=1, page_size=20, search=None, is_active=None):
    """Fetch paginated, filtered list of customer organizations."""
    query = Organization.query.filter_by(is_deleted=False)
    if is_active is not None:
      query = query.filter_by(is_active=is_active)
    if search:
      query = query.filter(Organization.organization_name.ilike(f"%{search}%"))
    
    # Sort by name
    query = query.order_by(Organization.organization_name.asc())
    paginated = query.paginate(page=page, per_page=page_size, error_out=False)
    return paginated

  def get_by_id(self, org_id: uuid.UUID) -> Organization:
    org = self.repository.get(org_id)
    if not org or org.is_deleted:
      raise NotFoundException("Organization not found.", code="ERR_NOT_FOUND")
    return org

  def create(self, data: dict) -> Organization:
    team_member_id = self._get_team_member_id()

    if "organization_name" not in data or not data.get("organization_name"):
      raise BusinessException(
        "Organization name is required.",
        code="ERR_VALIDATION"
      )

    org_type_id = data.get("organization_type_id")
    if org_type_id:
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
    else:
      org_type = OrganizationType.query.filter_by(is_active=True).first()
      if not org_type:
        org_type = OrganizationType(code="COLLEGE", name="College / University", is_active=True)
        db.session.add(org_type)
        db.session.flush()
      org_type_id = org_type.id

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
    db.session.flush()

    # Sync divisions
    if "divisions" in data and data["divisions"] is not None:
      self.repository.sync_divisions(org, data["divisions"], team_member_id)

    # Sync contacts
    if "contact_persons" in data and data["contact_persons"] is not None:
      self.repository.sync_contact_persons(org, data["contact_persons"], team_member_id)

    self.commit()
    return org

  def update(self, org_id: uuid.UUID, data: dict) -> Organization:
    team_member_id = self._get_team_member_id()
    org = self.get_by_id(org_id)

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

    # Sync divisions
    if "divisions" in data and data["divisions"] is not None:
      self.repository.sync_divisions(org, data["divisions"], team_member_id)

    # Sync contacts
    if "contact_persons" in data and data["contact_persons"] is not None:
      self.repository.sync_contact_persons(org, data["contact_persons"], team_member_id)

    self.commit()
    return org

  def delete(self, org_id: uuid.UUID) -> None:
    team_member_id = self._get_team_member_id()
    org = self.get_by_id(org_id)
    org.is_deleted = True
    org.deleted_at = db.func.now()
    if team_member_id:
      org.deleted_by_team_member_id = team_member_id
    self.commit()

  def lookup(self):
    """Retrieve non-deleted active organizations for dropdowns."""
    orgs = Organization.query.filter_by(is_deleted=False, is_active=True).order_by(Organization.organization_name.asc()).all()
    return orgs

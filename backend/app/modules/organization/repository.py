import uuid
from datetime import datetime
from app.core.extensions import db
from app.infrastructure.persistence.base_repository import SQLAlchemyBaseRepository
from app.models import Organization, OrganizationDivision, ContactPerson


class OrganizationRepository(SQLAlchemyBaseRepository[Organization]):
    def __init__(self):
        super().__init__(Organization)

    def get_active(self) -> Organization | None:
        """Fetch the first active and non-deleted organization."""
        return self.model_class.query.filter_by(is_deleted=False).first()

    def sync_divisions(self, org: Organization, divisions_data: list[dict], team_member_id: uuid.UUID | None = None) -> None:
        """Syncs organization divisions using a delta approach (adds, updates, and deletes)."""
        existing_divisions = {div.id: div for div in org.divisions}
        updated_ids = set()

        for div_data in divisions_data:
            div_id = div_data.get("id")
            if div_id:
                try:
                    div_id = uuid.UUID(str(div_id))
                except ValueError:
                    div_id = None

            if div_id and div_id in existing_divisions:
                # Update existing division
                div = existing_divisions[div_id]
                div.department = div_data.get("department")
                div.course = div_data.get("course")
                div.section = div_data.get("section")
                div.year = div_data.get("year")
                div.semester = div_data.get("semester")
                div.batch = div_data.get("batch")
                if team_member_id:
                    div.updated_by_team_member_id = team_member_id
                updated_ids.add(div_id)
            else:
                # Create new division
                new_div = OrganizationDivision(
                    organization_id=org.id,
                    department=div_data.get("department"),
                    course=div_data.get("course"),
                    section=div_data.get("section"),
                    year=div_data.get("year"),
                    semester=div_data.get("semester"),
                    batch=div_data.get("batch")
                )
                if team_member_id:
                    new_div.created_by_team_member_id = team_member_id
                    new_div.updated_by_team_member_id = team_member_id
                org.divisions.append(new_div)

        # Delete divisions that are no longer present
        for div_id, div in existing_divisions.items():
            if div_id not in updated_ids:
                db.session.delete(div)

    def sync_contact_persons(self, org: Organization, contact_persons_data: list[dict], team_member_id: uuid.UUID | None = None) -> None:
        """Syncs organization contact persons (adds, updates, and soft deletes)."""
        existing_contacts = {c.id: c for c in org.contact_persons if not c.is_deleted}
        updated_ids = set()

        for contact_data in contact_persons_data:
            c_id = contact_data.get("id")
            if c_id:
                try:
                    c_id = uuid.UUID(str(c_id))
                except ValueError:
                    c_id = None

            if c_id and c_id in existing_contacts:
                # Update existing contact
                c = existing_contacts[c_id]
                c.name = contact_data.get("name")
                c.designation = contact_data.get("designation")
                c.phone = contact_data.get("phone")
                c.alternate_phone = contact_data.get("alternate_phone")
                c.email = contact_data.get("email")
                c.is_primary = contact_data.get("is_primary", False)
                c.preferred_contact_method = contact_data.get("preferred_contact_method")
                c.notes = contact_data.get("notes")
                c.is_active = contact_data.get("is_active", True)
                if team_member_id:
                    c.updated_by_team_member_id = team_member_id
                updated_ids.add(c_id)
            else:
                # Create new contact
                new_c = ContactPerson(
                    organization_id=org.id,
                    name=contact_data.get("name"),
                    designation=contact_data.get("designation"),
                    phone=contact_data.get("phone"),
                    alternate_phone=contact_data.get("alternate_phone"),
                    email=contact_data.get("email"),
                    is_primary=contact_data.get("is_primary", False),
                    preferred_contact_method=contact_data.get("preferred_contact_method"),
                    notes=contact_data.get("notes"),
                    is_active=contact_data.get("is_active", True)
                )
                if team_member_id:
                    new_c.created_by_team_member_id = team_member_id
                    new_c.updated_by_team_member_id = team_member_id
                org.contact_persons.append(new_c)

        # Soft delete contacts that are no longer present
        for c_id, c in existing_contacts.items():
            if c_id not in updated_ids:
                c.is_deleted = True
                c.deleted_at = datetime.utcnow()
                if team_member_id:
                    c.deleted_by_team_member_id = team_member_id

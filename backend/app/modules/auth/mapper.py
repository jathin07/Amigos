from __future__ import annotations

from typing import List

from app.models import TeamMember, UserAccount
from app.modules.auth.schemas.response import (
    PermissionDTO,
    UserSummary,
)


class AuthMapper:
    """
    Maps authentication domain models to API response DTOs.
    """

    @staticmethod
    def to_user_summary(
        user: UserAccount,
        team_member: TeamMember,
    ) -> UserSummary:
        """
        Convert UserAccount + TeamMember into UserSummary DTO.
        """

        role_name = (
            team_member.role.name
            if getattr(team_member, "role", None)
            else "Team Member"
        )

        return UserSummary(
            id=str(team_member.id),
            employee_code=team_member.employee_code or "",
            name=team_member.display_name,
            email=team_member.official_email or "",
            phone=team_member.phone,
            designation=team_member.designation or "",
            role=role_name,
            avatar_url=team_member.avatar_url,
            is_active=bool(
                user.is_active and team_member.is_active
            ),
            last_login_at=(
                user.last_login_at.isoformat()
                if user.last_login_at
                else None
            ),
        )

    @staticmethod
    def to_permissions(
        team_member: TeamMember,
    ) -> List[PermissionDTO]:
        """
        Maps a TeamMember's role into Permission DTOs.

        Phase 1:
        Permission data is inferred from role.

        Future:
        Replace with RolePermission repository lookup.
        """

        role_name = (
            team_member.role.name.lower()
            if getattr(team_member, "role", None)
            else ""
        )

        permissions_map = {
            "admin": [
                PermissionDTO(
                    code="admin.full",
                    name="Full Admin Access",
                    description="Administrative rights across all modules.",
                )
            ],
            "manager": [
                PermissionDTO(
                    code="booking.write",
                    name="Booking Management",
                    description="Create and manage bookings.",
                ),
                PermissionDTO(
                    code="lead.write",
                    name="Lead Management",
                    description="Manage CRM leads.",
                ),
            ],
            "team member": [
                PermissionDTO(
                    code="booking.write",
                    name="Booking Write",
                    description="Create and update bookings.",
                )
            ],
        }

        return permissions_map.get(
            role_name,
            [
                PermissionDTO(
                    code="booking.read",
                    name="Booking Read",
                    description="View booking information.",
                )
            ],
        )

    @staticmethod
    def to_role_name(team_member: TeamMember) -> str:
        """
        Returns the user's role name.
        """

        if getattr(team_member, "role", None):
            return team_member.role.name

        return "Team Member"
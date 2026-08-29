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

        role_key = (
            team_member.role.code.lower() if getattr(team_member, "role", None) and getattr(team_member.role, "code", None)
            else (team_member.role.name.lower() if getattr(team_member, "role", None) else "team_member")
        )

        admin_perms = [
            PermissionDTO(code="admin.full", name="Full Admin Access", description="Full administrative control."),
            PermissionDTO(code="crm.read", name="CRM Read", description="View CRM leads."),
            PermissionDTO(code="crm.write", name="CRM Write", description="Create and edit CRM leads."),
            PermissionDTO(code="crm.contacts.read", name="Contacts Read", description="View customer contacts."),
            PermissionDTO(code="crm.contacts.write", name="Contacts Write", description="Manage customer contacts."),
            PermissionDTO(code="proposal.read", name="Proposal Read", description="View proposals."),
            PermissionDTO(code="proposal.write", name="Proposal Write", description="Create and edit proposals."),
            PermissionDTO(code="booking.read", name="Booking Read", description="View bookings."),
            PermissionDTO(code="booking.write", name="Booking Write", description="Manage bookings."),
            PermissionDTO(code="operations.read", name="Operations Read", description="View operations."),
            PermissionDTO(code="operations.write", name="Operations Write", description="Manage operations."),
            PermissionDTO(code="vendor.read", name="Vendor Read", description="View vendors."),
            PermissionDTO(code="vendor.write", name="Vendor Write", description="Manage vendors."),
            PermissionDTO(code="finance.read", name="Finance Read", description="View financial records."),
            PermissionDTO(code="finance.write", name="Finance Write", description="Manage financial transactions."),
            PermissionDTO(code="package.read", name="Package Read", description="View packages."),
            PermissionDTO(code="package.write", name="Package Write", description="Manage packages."),
            PermissionDTO(code="reports.read", name="Reports Read", description="View reports."),
            PermissionDTO(code="master.read", name="Master Data Read", description="View master catalog."),
            PermissionDTO(code="master.write", name="Master Data Write", description="Manage master catalog."),
        ]

        team_member_perms = [
            PermissionDTO(code="crm.read", name="CRM Read", description="View CRM leads."),
            PermissionDTO(code="crm.write", name="CRM Write", description="Create and edit CRM leads."),
            PermissionDTO(code="crm.contacts.read", name="Contacts Read", description="View customer contacts."),
            PermissionDTO(code="crm.contacts.write", name="Contacts Write", description="Manage customer contacts."),
            PermissionDTO(code="proposal.read", name="Proposal Read", description="View proposals."),
            PermissionDTO(code="proposal.write", name="Proposal Write", description="Create and edit proposals."),
            PermissionDTO(code="booking.read", name="Booking Read", description="View bookings."),
            PermissionDTO(code="booking.write", name="Booking Write", description="Manage bookings."),
            PermissionDTO(code="operations.read", name="Operations Read", description="View operations."),
            PermissionDTO(code="operations.write", name="Operations Write", description="Manage operations."),
            PermissionDTO(code="vendor.read", name="Vendor Read", description="View vendors."),
            PermissionDTO(code="vendor.write", name="Vendor Write", description="Manage vendors."),
            PermissionDTO(code="finance.read", name="Finance Read", description="View financial records."),
            PermissionDTO(code="finance.write", name="Finance Write", description="Manage financial transactions."),
            PermissionDTO(code="package.read", name="Package Read", description="View packages."),
            PermissionDTO(code="reports.read", name="Reports Read", description="View reports."),
        ]

        operations_perms = [
            PermissionDTO(code="crm.read", name="CRM Read", description="View CRM leads."),
            PermissionDTO(code="crm.write", name="CRM Write", description="Create and edit CRM leads."),
            PermissionDTO(code="crm.contacts.read", name="Contacts Read", description="View customer contacts."),
            PermissionDTO(code="booking.read", name="Booking Read", description="View bookings."),
            PermissionDTO(code="booking.write", name="Booking Write", description="Manage bookings."),
            PermissionDTO(code="operations.read", name="Operations Read", description="View operations."),
            PermissionDTO(code="operations.write", name="Operations Write", description="Manage operations."),
        ]

        if "admin" in role_key or "super" in role_key:
            return admin_perms
        elif "op" in role_key:
            return operations_perms
        else:
            return team_member_perms

    @staticmethod
    def to_role_name(team_member: TeamMember) -> str:
        """
        Returns the user's role name.
        """

        if getattr(team_member, "role", None):
            return team_member.role.name

        return "Team Member"
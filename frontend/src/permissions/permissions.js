export const PERMISSIONS = {
  // CRM & Leads
  CRM_READ: "crm.read",
  CRM_CREATE: "crm.create",
  CRM_UPDATE: "crm.update",

  // Proposals & Quotations
  PROPOSAL_READ: "proposal.read",
  PROPOSAL_CREATE: "proposal.create",
  PROPOSAL_UPDATE: "proposal.update",

  // Bookings & Travelers
  BOOKING_READ: "booking.read",
  BOOKING_CREATE: "booking.create",
  BOOKING_UPDATE: "booking.update",

  // Operations & Tasks
  OPERATIONS_READ: "operations.read",
  OPERATIONS_UPDATE: "operations.update",

  // Finance & Ledger
  FINANCE_READ: "finance.read",
  FINANCE_WRITE: "finance.write",

  // Vendors
  VENDOR_READ: "vendor.read",
  VENDOR_CREATE: "vendor.create",
  VENDOR_UPDATE: "vendor.update",

  // Reports
  REPORTS_READ: "reports.read",

  // Packages Catalog
  PACKAGE_READ: "package.read",
  PACKAGE_CREATE: "package.create",
  PACKAGE_UPDATE: "package.update",

  // Masters
  MASTERS_READ: "masters.read",
  MASTERS_WRITE: "masters.write",

  // Team
  TEAM_READ: "team.read",
  TEAM_WRITE: "team.write",

  // Global Admin Bypass
  ADMIN_FULL: "admin.full",
};

/**
 * Checks if user has a specific permission claim.
 * Superadmins with "admin.full" automatically bypass all checks.
 */
export function hasPermissionClaim(userPermissions, requiredPermission) {
  if (!userPermissions || !Array.isArray(userPermissions)) return false;
  if (userPermissions.includes(PERMISSIONS.ADMIN_FULL)) return true;
  return userPermissions.includes(requiredPermission);
}

/**
 * Checks if user has all required permission claims.
 */
export function hasAllPermissionClaims(userPermissions, requiredPermissions = []) {
  if (requiredPermissions.length === 0) return true;
  return requiredPermissions.every((perm) => hasPermissionClaim(userPermissions, perm));
}

/**
 * Checks if user has at least one of the required permission claims.
 */
export function hasAnyPermissionClaims(userPermissions, requiredPermissions = []) {
  if (requiredPermissions.length === 0) return true;
  return requiredPermissions.some((perm) => hasPermissionClaim(userPermissions, perm));
}

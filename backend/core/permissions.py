from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsClientReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method not in SAFE_METHODS:
            return False
        return request.user.is_authenticated and getattr(
            request.user, "portal", ""
        ) in ("client", "both")


class IsBackendUser(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return getattr(request.user, "portal", "") in ("backend", "both")


class RolePermission(BasePermission):
    allowed_roles = set()

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        roles = set(getattr(request.user, "roles", []) or [])
        if "system_admin" in roles:
            return True
        if "viewer" in roles and request.method in SAFE_METHODS:
            return True
        if request.method not in SAFE_METHODS and "viewer" in roles:
            roles.remove("viewer")
        return bool(roles & self.allowed_roles)


class PropertyManagerRole(RolePermission):
    allowed_roles = {"property_manager"}


class FinancialAnalystRole(RolePermission):
    allowed_roles = {"financial_analyst"}

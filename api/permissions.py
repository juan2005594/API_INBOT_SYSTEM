from rest_framework import permissions

class IsAdminOrWarehouse(permissions.BasePermission):
    """
    Permiso para permitir el acceso solo a usuarios que son administradores o pertenecen al grupo 'Bodeguero'.
    """
    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or request.user.groups.filter(name='Bodeguero').exists())

class IsSeller(permissions.BasePermission):
    """
    Permiso para permitir el acceso solo a usuarios que pertenecen al grupo 'Vendedor'.
    """
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='Vendedor').exists()

class IsAdmin(permissions.BasePermission):
    """
    Permiso para permitir el acceso solo a usuarios que son superusuarios o miembros del staff.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff 
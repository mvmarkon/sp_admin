from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado que solo permite a los propietarios de un objeto editarlo.
    """

    def has_object_permission(self, request, view, obj):
        # Permisos de lectura para cualquier request,
        # así que siempre permitimos GET, HEAD o OPTIONS.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Permisos de escritura solo para el propietario del objeto.
        # Asumimos que el modelo tiene un atributo 'owner'.
        return obj.owner == request.user


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Permiso que permite lectura a todos pero escritura solo al staff.
    """

    def has_permission(self, request, view):
        # Permisos de lectura para cualquier request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Permisos de escritura solo para usuarios staff
        return request.user and request.user.is_staff


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso que permite lectura a todos pero escritura solo a administradores.
    """

    def has_permission(self, request, view):
        # Permisos de lectura para cualquier request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Permisos de escritura solo para superusuarios
        return request.user and request.user.is_superuser


class InventoryManagerPermission(permissions.BasePermission):
    """
    Permiso personalizado para gestores de inventario.

    - Lectura: Todos los usuarios autenticados
    - Escritura: Solo usuarios con permisos específicos o staff
    - Eliminación: Solo administradores
    """

    def has_permission(self, request, view):
        # Requiere autenticación para todas las operaciones
        if not request.user or not request.user.is_authenticated:
            return False

        # Permisos de lectura para usuarios autenticados
        if request.method in permissions.SAFE_METHODS:
            return True

        # Permisos de escritura para staff o usuarios con permisos específicos
        if request.method in ["POST", "PUT", "PATCH"]:
            return (
                request.user.is_staff
                or request.user.has_perm("products.change_product")
                or request.user.has_perm("products.add_product")
            )

        # Permisos de eliminación solo para administradores
        if request.method == "DELETE":
            return request.user.is_superuser or request.user.has_perm(
                "products.delete_product"
            )

        return False


class StockUpdatePermission(permissions.BasePermission):
    """
    Permiso específico para actualización de stock.
    """

    def has_permission(self, request, view):
        # Requiere autenticación
        if not request.user or not request.user.is_authenticated:
            return False

        # Permite a usuarios staff o con permisos específicos
        return (
            request.user.is_staff
            or request.user.has_perm("products.change_product")
            or request.user.groups.filter(name="Inventory Managers").exists()
        )


class ReadOnlyOrAuthenticated(permissions.BasePermission):
    """
    Permiso que permite lectura a todos y escritura a usuarios autenticados.
    """

    def has_permission(self, request, view):
        # Permisos de lectura para cualquier request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Permisos de escritura para usuarios autenticados
        return request.user and request.user.is_authenticated


class CategoryPermission(permissions.BasePermission):
    """
    Permisos específicos para categorías.
    """

    def has_permission(self, request, view):
        # Lectura libre para categorías
        if request.method in permissions.SAFE_METHODS:
            return True

        # Escritura requiere autenticación y permisos específicos
        if not request.user or not request.user.is_authenticated:
            return False

        return (
            request.user.is_staff
            or request.user.has_perm("products.add_category")
            or request.user.has_perm("products.change_category")
        )

    def has_object_permission(self, request, view, obj):
        # Lectura libre
        if request.method in permissions.SAFE_METHODS:
            return True

        # Escritura requiere permisos específicos
        if request.method in ["PUT", "PATCH"]:
            return request.user.is_staff or request.user.has_perm(
                "products.change_category"
            )

        # Eliminación solo para administradores
        if request.method == "DELETE":
            return request.user.is_superuser or request.user.has_perm(
                "products.delete_category"
            )

        return False

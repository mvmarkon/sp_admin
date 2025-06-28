import django_filters
from django.db.models import Q
from products.models import Product, Category


class ProductFilter(django_filters.FilterSet):
    """
    Filtros avanzados para productos.
    """

    # Filtros básicos
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.filter(is_active=True, is_deleted=False),
        field_name="category",
        help_text="Filtrar por categoría",
    )

    size = django_filters.ChoiceFilter(
        choices=Product.SIZES, field_name="size", help_text="Filtrar por talla"
    )

    color = django_filters.ChoiceFilter(
        choices=Product.COLORS, field_name="color", help_text="Filtrar por color"
    )

    # Filtros de precio
    min_price = django_filters.NumberFilter(
        field_name="price", lookup_expr="gte", help_text="Precio mínimo"
    )

    max_price = django_filters.NumberFilter(
        field_name="price", lookup_expr="lte", help_text="Precio máximo"
    )

    price_range = django_filters.RangeFilter(
        field_name="price", help_text="Rango de precios (ej: 100,500)"
    )

    # Filtros de stock
    min_stock = django_filters.NumberFilter(
        field_name="stock", lookup_expr="gte", help_text="Stock mínimo"
    )

    max_stock = django_filters.NumberFilter(
        field_name="stock", lookup_expr="lte", help_text="Stock máximo"
    )

    in_stock = django_filters.BooleanFilter(
        method="filter_in_stock",
        help_text="Filtrar solo productos con stock disponible",
    )

    low_stock = django_filters.BooleanFilter(
        method="filter_low_stock", help_text="Filtrar productos con stock bajo"
    )

    out_of_stock = django_filters.BooleanFilter(
        method="filter_out_of_stock", help_text="Filtrar productos agotados"
    )

    # Filtros de estado
    is_active = django_filters.BooleanFilter(
        field_name="is_active", help_text="Filtrar por productos activos/inactivos"
    )

    # Filtros de fecha
    created_after = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
        help_text="Productos creados después de esta fecha",
    )

    created_before = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="lte",
        help_text="Productos creados antes de esta fecha",
    )

    updated_after = django_filters.DateTimeFilter(
        field_name="updated_at",
        lookup_expr="gte",
        help_text="Productos actualizados después de esta fecha",
    )

    # Filtro de búsqueda avanzada
    search = django_filters.CharFilter(
        method="filter_search",
        help_text="Búsqueda en nombre, SKU, descripción y código de barras",
    )

    # Filtros por múltiples valores
    sizes = django_filters.BaseInFilter(
        field_name="size", help_text="Múltiples tallas separadas por coma (ej: S,M,L)"
    )

    colors = django_filters.BaseInFilter(
        field_name="color",
        help_text="Múltiples colores separados por coma (ej: RED,BLUE,GREEN)",
    )

    categories = django_filters.BaseInFilter(
        field_name="category",
        help_text="Múltiples categorías por ID separadas por coma (ej: 1,2,3)",
    )

    class Meta:
        model = Product
        fields = {
            "sku": ["exact", "icontains"],
            "name": ["exact", "icontains"],
            "barcode": ["exact", "icontains"],
            "price": ["exact", "lt", "lte", "gt", "gte"],
            "stock": ["exact", "lt", "lte", "gt", "gte"],
            "is_active": ["exact"],
        }

    def filter_in_stock(self, queryset, name, value):
        """
        Filtra productos que tienen stock disponible.
        """
        if value:
            return queryset.filter(stock__gt=0)
        return queryset.filter(stock=0)

    def filter_low_stock(self, queryset, name, value):
        """
        Filtra productos con stock bajo.
        """
        if value:
            # Productos donde stock <= min_stock
            return queryset.extra(where=["stock <= min_stock"])
        return queryset.extra(where=["stock > min_stock"])

    def filter_out_of_stock(self, queryset, name, value):
        """
        Filtra productos agotados.
        """
        if value:
            return queryset.filter(stock=0)
        return queryset.filter(stock__gt=0)

    def filter_search(self, queryset, name, value):
        """
        Búsqueda avanzada en múltiples campos.
        """
        if value:
            return queryset.filter(
                Q(name__icontains=value)
                | Q(sku__icontains=value)
                | Q(description__icontains=value)
                | Q(barcode__icontains=value)
                | Q(category__name__icontains=value)
            ).distinct()
        return queryset


class CategoryFilter(django_filters.FilterSet):
    """
    Filtros para categorías.
    """

    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
        help_text="Buscar por nombre de categoría",
    )

    is_active = django_filters.BooleanFilter(
        field_name="is_active", help_text="Filtrar categorías activas/inactivas"
    )

    has_products = django_filters.BooleanFilter(
        method="filter_has_products",
        help_text="Filtrar categorías que tienen productos",
    )

    created_after = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
        help_text="Categorías creadas después de esta fecha",
    )

    class Meta:
        model = Category
        fields = {
            "name": ["exact", "icontains"],
            "is_active": ["exact"],
        }

    def filter_has_products(self, queryset, name, value):
        """
        Filtra categorías que tienen productos activos.
        """
        if value:
            return queryset.filter(
                products__is_active=True, products__is_deleted=False
            ).distinct()
        return queryset.exclude(
            products__is_active=True, products__is_deleted=False
        ).distinct()

from django.contrib import admin
from django.utils.html import format_html
from core.admin import BaseModelAdmin
from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "order")
    readonly_fields = ("created_at",)


@admin.register(Category)
class CategoryAdmin(BaseModelAdmin):
    list_display = (
        "name",
        "active_products_count",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_active", "created_at", "updated_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = (
        "created_at",
        "updated_at",
        "deleted_at",
        "active_products_count",
    )

    fieldsets = (
        ("Información Básica", {"fields": ("name", "slug", "description")}),
        ("Estado", {"fields": ("is_active",)}),
        (
            "Metadatos",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "deleted_at",
                    "active_products_count",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    actions = ["activate_categories", "deactivate_categories"] + BaseModelAdmin.actions

    def activate_categories(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} categorías activadas exitosamente.")

    activate_categories.short_description = "Activar categorías seleccionadas"

    def deactivate_categories(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} categorías desactivadas exitosamente.")

    deactivate_categories.short_description = "Desactivar categorías seleccionadas"


@admin.register(Product)
class ProductAdmin(BaseModelAdmin):
    list_display = (
        "sku",
        "name",
        "category",
        "size",
        "color",
        "price",
        "stock",
        "stock_display",
        "stock_status_display",
        "is_active",
        "created_at",
    )
    list_filter = ("category", "size", "color", "is_active", "created_at", "updated_at")
    search_fields = ("sku", "name", "barcode", "description")
    list_editable = ("price", "stock", "is_active")
    list_per_page = 25

    fieldsets = (
        ("Información Básica", {"fields": ("name", "sku", "category", "description")}),
        ("Características", {"fields": ("size", "color", "barcode")}),
        ("Precios e Inventario", {"fields": ("price", "cost", "stock", "min_stock")}),
        ("Imagen", {"fields": ("image", "image_preview")}),
        ("Estado", {"fields": ("is_active",)}),
        (
            "Metadatos",
            {
                "fields": ("created_at", "updated_at", "deleted_at"),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ("created_at", "updated_at", "deleted_at", "image_preview")

    inlines = [ProductImageInline]

    actions = [
        "activate_products",
        "deactivate_products",
        "mark_as_low_stock",
        "bulk_update_stock",
    ] + BaseModelAdmin.actions

    def stock_display(self, obj):
        """Muestra el stock con formato y color."""
        if obj.is_out_of_stock:
            color = "red"
            icon = "❌"
        elif obj.is_low_stock:
            color = "orange"
            icon = "⚠️"
        else:
            color = "green"
            icon = "✅"

            return format_html(
                '<span style="color: {};"><strong>{}</strong> {} unidades</span>',
                color,
                icon,
                obj.stock,
            )

    stock_display.short_description = "Stock"
    stock_display.admin_order_field = "stock"

    def stock_status_display(self, obj):
        """Muestra el estado del stock con color."""
        status = obj.get_stock_status()
        color = obj.get_stock_status_color()

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>', color, status
        )

    stock_status_display.short_description = "Estado Stock"

    def image_preview(self, obj):
        """Muestra una vista previa de la imagen del producto."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;"/>',
                obj.image.url,
            )
        return "Sin imagen"

    image_preview.short_description = "Vista Previa"

    def activate_products(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} productos activados exitosamente.")

    activate_products.short_description = "Activar productos seleccionados"

    def deactivate_products(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} productos desactivados exitosamente.")

    deactivate_products.short_description = "Desactivar productos seleccionados"

    def mark_as_low_stock(self, request, queryset):
        count = 0
        for product in queryset:
            if product.stock <= product.min_stock:
                count += 1

            self.message_user(
                request, f"{count} productos identificados con stock bajo."
            )

    mark_as_low_stock.short_description = "Identificar productos con stock bajo"

    def bulk_update_stock(self, request, queryset):
        # Esta acción redirigirá a una vista personalizada para actualización masiva
        selected = queryset.values_list("pk", flat=True)
        return format_html(
            '<script>alert("Funcionalidad de actualización masiva en desarrollo. '
            'IDs seleccionados: {}");</script>',
            list(selected),
        )

    bulk_update_stock.short_description = "Actualización masiva de stock"

    def get_queryset(self, request):
        """Optimiza las consultas incluyendo relaciones."""
        qs = super().get_queryset(request)
        return qs.select_related("category")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtra las categorías activas en el formulario."""
        if db_field.name == "category":
            kwargs["queryset"] = Category.objects.filter(
                is_active=True, is_deleted=False
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ProductImage)
class ProductImageAdmin(BaseModelAdmin):
    list_display = ("product", "image_preview", "alt_text", "order", "created_at")
    list_filter = ("created_at", "product__category")
    search_fields = ("product__name", "product__sku", "alt_text")
    list_editable = ("order",)

    def image_preview(self, obj):
        """Muestra una vista previa de la imagen."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;"/>',
                obj.image.url,
            )
        return "Sin imagen"

    image_preview.short_description = "Vista Previa"

    def get_queryset(self, request):
        """Optimiza las consultas incluyendo el producto."""
        qs = super().get_queryset(request)
        return qs.select_related("product")


# Personalización adicional del admin
admin.site.site_header = "SanPedrito - Administración"
admin.site.site_title = "SanPedrito Admin"
admin.site.index_title = "Panel de Control - Inventario SanPedrito"

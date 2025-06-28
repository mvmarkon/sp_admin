from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from . import views

# Router para ViewSets (si los necesitamos en el futuro)
router = DefaultRouter()

# URLs de la API
urlpatterns = [
    # Autenticación JWT
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("me/", views.CurrentUserView.as_view(), name="current-user"),
    # Categorías
    path(
        "categories/",
        views.CategoryListCreateView.as_view(),
        name="category-list-create",
    ),
    path(
        "categories/<slug:slug>/",
        views.CategoryDetailView.as_view(),
        name="category-detail",
    ),
    # Productos
    path(
        "products/", views.ProductListCreateView.as_view(), name="product-list-create"
    ),
    path(
        "products/<str:sku>/", views.ProductDetailView.as_view(), name="product-detail"
    ),
    # Gestión de stock
    path(
        "products/<str:sku>/update-stock/",
        views.update_product_stock,
        name="product-update-stock",
    ),
    path(
        "products/bulk-update/", views.bulk_update_products, name="product-bulk-update"
    ),
    # Con
    # sultas especiales
    path(
        "products/alerts/low-stock/",
        views.low_stock_products,
        name="low-stock-products",
    ),
    path(
        "products/alerts/out-of-stock/",
        views.out_of_stock_products,
        name="out-of-stock-products",
    ),
    # Estadísticas y reportes
    path("inventory/stats/", views.inventory_stats, name="inventory-stats"),
    # Búsqueda
    path("search/products/", views.search_products, name="search-products"),
    # Incluir URLs del router (para futuras extensiones)
    path("", include(router.urls)),
]

# Nombres de las URLs para referencia
app_name = "api"

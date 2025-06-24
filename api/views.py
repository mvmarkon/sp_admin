from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from products.models import Category, Product
from .serializers import (
    UserSerializer,
    CategorySerializer,
    CategoryListSerializer,
    ProductSerializer,
    ProductListSerializer,
    ProductStockUpdateSerializer,
    ProductBulkUpdateSerializer,
    ProductSearchSerializer
)
from .filters import ProductFilter
from .permissions import IsOwnerOrReadOnly


class CategoryListCreateView(generics.ListCreateAPIView):
    """
    Vista para listar y crear categorías.
    
    GET: Lista todas las categorías activas
    POST: Crea una nueva categoría (requiere autenticación)
    """
    queryset = Category.objects.filter(is_deleted=False)
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CategoryListSerializer
        return CategorySerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.method == 'GET':
            # Solo mostrar categorías activas en GET
            queryset = queryset.filter(is_active=True)
        return queryset.order_by('name')


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista para obtener, actualizar y eliminar una categoría específica.
    """
    queryset = Category.objects.filter(is_deleted=False)
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    
    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class ProductListCreateView(generics.ListCreateAPIView):
    """
    Vista para listar y crear productos.
    
    GET: Lista productos con filtros opcionales
    POST: Crea un nuevo producto (requiere autenticación)
    """
    queryset = Product.objects.filter(is_deleted=False)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'sku', 'description', 'barcode']
    ordering_fields = ['name', 'price', 'stock', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductListSerializer
        return ProductSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('category')
        
        if self.request.method == 'GET':
            # Solo mostrar productos activos en GET por defecto
            show_inactive = self.request.query_params.get('show_inactive', 'false').lower() == 'true'
            if not show_inactive:
                queryset = queryset.filter(is_active=True)
        
        return queryset
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='category',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filtrar por ID de categoría'
            ),
            OpenApiParameter(
                name='size',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filtrar por talla'
            ),
            OpenApiParameter(
                name='color',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filtrar por color'
            ),
            OpenApiParameter(
                name='in_stock',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filtrar solo productos con stock'
            ),
            OpenApiParameter(
                name='low_stock',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filtrar productos con stock bajo'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Buscar en nombre, SKU, descripción o código de barras'
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista para obtener, actualizar y eliminar un producto específico.
    """
    queryset = Product.objects.filter(is_deleted=False)
    serializer_class = ProductSerializer
    lookup_field = 'sku'
    
    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        return super().get_queryset().select_related('category').prefetch_related('additional_images')


@extend_schema(
    request=ProductStockUpdateSerializer,
    responses={200: ProductSerializer},
    description="Actualiza el stock de un producto específico"
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_product_stock(request, sku):
    """
    Actualiza el stock de un producto específico.
    
    Permite agregar o quitar stock con validaciones de seguridad.
    """
    product = get_object_or_404(Product, sku=sku, is_deleted=False)
    
    serializer = ProductStockUpdateSerializer(
        data=request.data,
        context={'product': product}
    )
    
    if serializer.is_valid():
        quantity = serializer.validated_data['quantity']
        operation = serializer.validated_data['operation']
        reason = serializer.validated_data.get('reason', '')
        
        # Actualizar stock
        success = product.update_stock(quantity, operation)
        
        if success:
            # Log de la operación (opcional)
            action = "agregado" if operation == 'add' else "quitado"
            message = f"Stock {action}: {quantity} unidades. Stock actual: {product.stock}"
            if reason:
                message += f" Razón: {reason}"
            
            # Retornar producto actualizado
            product_serializer = ProductSerializer(product)
            
            return Response({
                'message': message,
                'product': product_serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'No hay suficiente stock para realizar la operación'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=ProductBulkUpdateSerializer,
    responses={200: {'description': 'Productos actualizados exitosamente'}},
    description="Actualización masiva de productos"
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def bulk_update_products(request):
    """
    Actualización masiva de productos.
    
    Permite actualizar múltiples productos a la vez.
    """
    serializer = ProductBulkUpdateSerializer(data=request.data)
    
    if serializer.is_valid():
        product_ids = serializer.validated_data['product_ids']
        updates = serializer.validated_data['updates']
        
        # Filtrar productos existentes y no eliminados
        products = Product.objects.filter(
            id__in=product_ids,
            is_deleted=False
        )
        
        if not products.exists():
            return Response({
                'error': 'No se encontraron productos válidos para actualizar'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Realizar actualización masiva
        updated_count = products.update(**updates)
        
        return Response({
            'message': f'{updated_count} productos actualizados exitosamente',
            'updated_products': list(products.values_list('id', flat=True))
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    responses={200: ProductListSerializer(many=True)},
    description="Obtiene productos con stock bajo"
)
class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

@api_view(['GET'])
@permission_classes([AllowAny])
def low_stock_products(request):
    """
    Retorna productos con stock bajo.
    """
    products = Product.objects.filter(
        is_deleted=False,
        is_active=True
    ).select_related('category')
    
    # Filtrar productos con stock bajo
    low_stock_products = [p for p in products if p.is_low_stock]
    
    serializer = ProductListSerializer(low_stock_products, many=True)
    
    return Response({
        'count': len(low_stock_products),
        'products': serializer.data
    }, status=status.HTTP_200_OK)


@extend_schema(
    responses={200: ProductListSerializer(many=True)},
    description="Obtiene productos agotados"
)
@api_view(['GET'])
@permission_classes([AllowAny])
def out_of_stock_products(request):
    """
    Retorna productos agotados.
    """
    products = Product.objects.filter(
        stock=0,
        is_deleted=False,
        is_active=True
    ).select_related('category')
    
    serializer = ProductListSerializer(products, many=True)
    
    return Response({
        'count': products.count(),
        'products': serializer.data
    }, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='category_id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='ID de la categoría (opcional)'
        )
    ],
    responses={200: {'description': 'Estadísticas del inventario'}},
    description="Obtiene estadísticas generales del inventario"
)
@api_view(['GET'])
@permission_classes([AllowAny])
def inventory_stats(request):
    """
    Retorna estadísticas generales del inventario.
    """
    category_id = request.query_params.get('category_id')
    
    # Base queryset
    products = Product.objects.filter(is_deleted=False, is_active=True)
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Calcular estadísticas
    total_products = products.count()
    total_stock = sum(p.stock for p in products)
    low_stock_count = len([p for p in products if p.is_low_stock])
    out_of_stock_count = products.filter(stock=0).count()
    
    # Valor total del inventario
    total_value = sum(p.price * p.stock for p in products)
    
    # Productos por categoría
    categories_stats = {}
    for product in products.select_related('category'):
        cat_name = product.category.name
        if cat_name not in categories_stats:
            categories_stats[cat_name] = {
                'count': 0,
                'total_stock': 0,
                'total_value': 0
            }
        categories_stats[cat_name]['count'] += 1
        categories_stats[cat_name]['total_stock'] += product.stock
        categories_stats[cat_name]['total_value'] += product.price * product.stock
    
    return Response({
        'total_products': total_products,
        'total_stock': total_stock,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'total_inventory_value': float(total_value),
        'categories_stats': categories_stats,
        'stock_alerts': {
            'low_stock_percentage': (low_stock_count / total_products * 100) if total_products > 0 else 0,
            'out_of_stock_percentage': (out_of_stock_count / total_products * 100) if total_products > 0 else 0
        }
    }, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='q',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Término de búsqueda',
            required=True
        )
    ],
    responses={200: ProductListSerializer(many=True)},
    description="Búsqueda avanzada de productos"
)
@api_view(['GET'])
@permission_classes([AllowAny])
def search_products(request):
    """
    Búsqueda avanzada de productos.
    
    Busca en nombre, SKU, descripción y código de barras.
    """
    query = request.query_params.get('q', '').strip()
    
    if not query:
        return Response({
            'error': 'Parámetro de búsqueda "q" es requerido'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Búsqueda en múltiples campos
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(sku__icontains=query) |
        Q(description__icontains=query) |
        Q(barcode__icontains=query) |
        Q(category__name__icontains=query),
        is_deleted=False,
        is_active=True
    ).select_related('category').distinct()
    
    serializer = ProductListSerializer(products, many=True)
    
    return Response({
        'query': query,
        'count': products.count(),
        'products': serializer.data
    }, status=status.HTTP_200_OK)
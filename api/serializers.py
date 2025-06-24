from django.contrib.auth import get_user_model
from rest_framework import serializers
from products.models import Category, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Category.
    """
    active_products_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'description',
            'slug',
            'is_active',
            'active_products_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Serializador simplificado para listar categorías.
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializador para imágenes adicionales de productos.
    """
    class Meta:
        model = ProductImage
        fields = [
            'id',
            'image',
            'alt_text',
            'order'
        ]


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializador completo para el modelo Product.
    """
    category = CategoryListSerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    additional_images = ProductImageSerializer(many=True, read_only=True)
    
    # Campos calculados
    is_low_stock = serializers.ReadOnlyField()
    is_out_of_stock = serializers.ReadOnlyField()
    stock_status = serializers.SerializerMethodField()
    profit_margin = serializers.ReadOnlyField()
    
    # Campos con formato personalizado
    size_display = serializers.CharField(source='get_size_display', read_only=True)
    color_display = serializers.CharField(source='get_color_display', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id',
            'sku',
            'name',
            'description',
            'category',
            'category_id',
            'size',
            'size_display',
            'color',
            'color_display',
            'price',
            'cost',
            'stock',
            'min_stock',
            'is_active',
            'image',
            'additional_images',
            'barcode',
            'is_low_stock',
            'is_out_of_stock',
            'stock_status',
            'profit_margin',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'sku',
            'created_at',
            'updated_at',
            'is_low_stock',
            'is_out_of_stock',
            'profit_margin'
        ]
    
    def get_stock_status(self, obj):
        """Retorna el estado del stock."""
        return obj.get_stock_status()
    
    def validate_stock(self, value):
        """Valida que el stock no sea negativo."""
        if value < 0:
            raise serializers.ValidationError(
                "El stock no puede ser negativo."
            )
        return value
    
    def validate_price(self, value):
        """Valida que el precio sea mayor a 0."""
        if value <= 0:
            raise serializers.ValidationError(
                "El precio debe ser mayor a 0."
            )
        return value
    
    def validate_cost(self, value):
        """Valida que el costo no sea negativo."""
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "El costo no puede ser negativo."
            )
        return value
    
    def validate(self, data):
        """Validaciones a nivel de objeto."""
        # Validar que el costo no sea mayor al precio
        cost = data.get('cost')
        price = data.get('price')
        
        if cost is not None and price is not None and cost > price:
            raise serializers.ValidationError(
                "El costo no puede ser mayor al precio de venta."
            )
        
        return data


class ProductListSerializer(serializers.ModelSerializer):
    """
    Serializador simplificado para listar productos.
    """
    category = serializers.StringRelatedField()
    size_display = serializers.CharField(source='get_size_display', read_only=True)
    color_display = serializers.CharField(source='get_color_display', read_only=True)
    stock_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id',
            'sku',
            'name',
            'category',
            'size',
            'size_display',
            'color',
            'color_display',
            'price',
            'stock',
            'stock_status',
            'is_active',
            'image'
        ]
    
    def get_stock_status(self, obj):
        return obj.get_stock_status()


class ProductStockUpdateSerializer(serializers.Serializer):
    """
    Serializador para actualizar el stock de un producto.
    """
    quantity = serializers.IntegerField(
        min_value=1,
        help_text="Cantidad a agregar o quitar del stock"
    )
    operation = serializers.ChoiceField(
        choices=[('add', 'Agregar'), ('subtract', 'Quitar')],
        default='add',
        help_text="Operación a realizar: 'add' para agregar, 'subtract' para quitar"
    )
    reason = serializers.CharField(
        max_length=200,
        required=False,
        help_text="Razón del ajuste de stock (opcional)"
    )
    
    def validate(self, data):
        """Validaciones para la actualización de stock."""
        quantity = data['quantity']
        operation = data['operation']
        
        # Obtener el producto del contexto
        product = self.context.get('product')
        
        if operation == 'subtract' and product and product.stock < quantity:
            raise serializers.ValidationError(
                f"No hay suficiente stock. Stock actual: {product.stock}, "
                f"cantidad solicitada: {quantity}"
            )
        
        return data


class ProductBulkUpdateSerializer(serializers.Serializer):
    """
    Serializador para actualización masiva de productos.
    """
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Lista de IDs de productos a actualizar"
    )
    updates = serializers.DictField(
        help_text="Diccionario con los campos a actualizar"
    )
    
    def validate_updates(self, value):
        """Valida que los campos a actualizar sean válidos."""
        allowed_fields = ['price', 'stock', 'min_stock', 'is_active']
        
        for field in value.keys():
            if field not in allowed_fields:
                raise serializers.ValidationError(
                    f"Campo '{field}' no permitido para actualización masiva. "
                    f"Campos permitidos: {allowed_fields}"
                )
        
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

class ProductSearchSerializer(serializers.Serializer):
    """
    Serializador para parámetros de búsqueda de productos.
    """
    search = serializers.CharField(
        required=False,
        help_text="Término de búsqueda (nombre, SKU, descripción)"
    )
    category = serializers.IntegerField(
        required=False,
        help_text="ID de la categoría"
    )
    size = serializers.ChoiceField(
        choices=Product.SIZES,
        required=False,
        help_text="Talla del producto"
    )
    color = serializers.ChoiceField(
        choices=Product.COLORS,
        required=False,
        help_text="Color del producto"
    )
    min_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text="Precio mínimo"
    )
    max_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text="Precio máximo"
    )
    in_stock = serializers.BooleanField(
        required=False,
        help_text="Filtrar solo productos con stock"
    )
    low_stock = serializers.BooleanField(
        required=False,
        help_text="Filtrar solo productos con stock bajo"
    )
    is_active = serializers.BooleanField(
        required=False,
        default=True,
        help_text="Filtrar por productos activos/inactivos"
    )
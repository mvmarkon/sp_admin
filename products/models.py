from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from core.models import BaseModel
import uuid


class Category(BaseModel):
    """
    Modelo para categorías de productos infantiles.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre",
        help_text="Nombre de la categoría (ej: Camisetas, Pantalones, Vestidos)",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción detallada de la categoría",
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        verbose_name="Slug",
        help_text="URL amigable generada automáticamente",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activa",
        help_text="Indica si la categoría está activa",
    )

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def active_products_count(self):
        """Retorna el número de productos activos en esta categoría."""
        return self.products.filter(is_active=True, is_deleted=False).count()


class Product(BaseModel):
    """
    Modelo para productos de ropa infantil.
    """

    # Choices para tallas
    SIZES = [
        ("0-3m", "0-3 meses"),
        ("3-6m", "3-6 meses"),
        ("6-9m", "6-9 meses"),
        ("9-12m", "9-12 meses"),
        ("12-18m", "12-18 meses"),
        ("18-24m", "18-24 meses"),
        ("2T", "2 años"),
        ("3T", "3 años"),
        ("4T", "4 años"),
        ("5T", "5 años"),
        ("6T", "6 años"),
        ("7T", "7 años"),
        ("8T", "8 años"),
        ("XS", "Extra Pequeño"),
        ("S", "Pequeño"),
        ("M", "Mediano"),
        ("L", "Grande"),
        ("XL", "Extra Grande"),
    ]

    # Choices para colores
    COLORS = [
        ("RED", "Rojo"),
        ("BLUE", "Azul"),
        ("GREEN", "Verde"),
        ("YELLOW", "Amarillo"),
        ("PINK", "Rosa"),
        ("PURPLE", "Morado"),
        ("ORANGE", "Naranja"),
        ("BLACK", "Negro"),
        ("WHITE", "Blanco"),
        ("GRAY", "Gris"),
        ("BROWN", "Café"),
        ("NAVY", "Azul Marino"),
        ("BEIGE", "Beige"),
        ("TURQUOISE", "Turquesa"),
        ("CORAL", "Coral"),
        ("MINT", "Menta"),
        ("MULTICOLOR", "Multicolor"),
    ]

    # Campos del modelo
    name = models.CharField(
        max_length=200,
        verbose_name="Nombre",
        help_text="Nombre descriptivo del producto",
    )
    sku = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="SKU",
        help_text="Código único del producto (Stock Keeping Unit)",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Categoría",
        help_text="Categoría a la que pertenece el producto",
    )
    size = models.CharField(
        max_length=10,
        choices=SIZES,
        verbose_name="Talla",
        help_text="Talla del producto",
    )
    color = models.CharField(
        max_length=20,
        choices=COLORS,
        verbose_name="Color",
        help_text="Color principal del producto",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name="Precio",
        help_text="Precio de venta del producto en pesos mexicanos",
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.00)],
        null=True,
        blank=True,
        verbose_name="Costo",
        help_text="Costo de adquisición del producto",
    )
    stock = models.PositiveIntegerField(
        default=0, verbose_name="Stock", help_text="Cantidad disponible en inventario"
    )
    min_stock = models.PositiveIntegerField(
        default=5,
        verbose_name="Stock Mínimo",
        help_text="Cantidad mínima antes de requerir reabastecimiento",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si el producto está disponible para venta",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción detallada del producto",
    )
    image = models.ImageField(
        upload_to="products/images/",
        null=True,
        blank=True,
        verbose_name="Imagen",
        help_text="Imagen principal del producto",
    )
    barcode = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Código de Barras",
        help_text="Código de barras del producto",
    )

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["size", "color"]),
            models.Index(fields=["stock"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.get_size_display()} - {self.get_color_display()}"

    def save(self, *args, **kwargs):
        # Generar SKU automáticamente si no existe
        if not self.sku:
            self.sku = self.generate_sku()
        super().save(*args, **kwargs)

    def generate_sku(self):
        """
        Genera un SKU único basado en categoría, talla y color.
        """
        category_code = self.category.name[:3].upper() if self.category else "GEN"
        size_code = self.size.replace("-", "").replace("T", "")
        color_code = self.color[:3]
        unique_id = str(uuid.uuid4())[:8].upper()

        return f"{category_code}-{size_code}-{color_code}-{unique_id}"

    @property
    def is_low_stock(self):
        """Indica si el producto tiene stock bajo."""
        return self.stock <= self.min_stock

    @property
    def is_out_of_stock(self):
        """Indica si el producto está agotado."""
        return self.stock == 0

    @property
    def profit_margin(self):
        """Calcula el margen de ganancia si se tiene el costo."""
        if self.cost and self.cost > 0:
            return ((self.price - self.cost) / self.cost) * 100
        return None

    def update_stock(self, quantity, operation="add"):
        """
        Actualiza el stock del producto.

            Args:
            quantity (int): Cantidad a agregar o quitar
            operation (str): 'add' para agregar, 'subtract' para quitar

            Returns:
            bool: True si la operación fue exitosa, False si no hay suficiente stock
        """
        if operation == "add":
            self.stock += quantity
        elif operation == "subtract":
            if self.stock >= quantity:
                self.stock -= quantity
            else:
                return False

            self.save()
        return True

    def get_stock_status(self):
        """
        Retorna el estado del stock como string.
        """
        if self.is_out_of_stock:
            return "Agotado"
        elif self.is_low_stock:
            return "Stock Bajo"
        else:
            return "Disponible"

    def get_stock_status_color(self):
        """
        Retorna un color CSS basado en el estado del stock.
        """
        if self.is_out_of_stock:
            return "red"
        elif self.is_low_stock:
            return "orange"
        else:
            return "green"


class ProductImage(BaseModel):
    """
    Modelo para múltiples imágenes de productos.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="additional_images",
        verbose_name="Producto",
    )
    image = models.ImageField(upload_to="products/gallery/", verbose_name="Imagen")
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Texto Alternativo",
        help_text="Descripción de la imagen para accesibilidad",
    )
    order = models.PositiveIntegerField(
        default=0, verbose_name="Orden", help_text="Orden de visualización de la imagen"
    )

    class Meta:
        verbose_name = "Imagen de Producto"
        verbose_name_plural = "Imágenes de Productos"
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"Imagen de {self.product.name}"

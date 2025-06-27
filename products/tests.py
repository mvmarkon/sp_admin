from django.test import TestCase
from django.db import IntegrityError
from decimal import Decimal
from products.models import Category, Product, ProductImage
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io


class CategoryModelTest(TestCase):
    """Tests para el modelo Category."""

    def setUp(self):
        """Configuración inicial para los tests."""
        self.category_data = {
            "name": "Camisetas",
            "description": "Camisetas para niños y niñas",
            "is_active": True,
        }

    def test_create_category(self):
        """Test para crear una categoría."""
        category = Category.objects.create(**self.category_data)
        self.assertEqual(category.name, "Camisetas")
        self.assertEqual(category.description, "Camisetas para niños y niñas")
        self.assertTrue(category.is_active)
        self.assertIsNotNone(category.created_at)
        self.assertIsNotNone(category.updated_at)
        self.assertFalse(category.is_deleted)

    def test_category_slug_generation(self):
        """Test para verificar la generación automática del slug."""
        category = Category.objects.create(**self.category_data)
        self.assertEqual(category.slug, "camisetas")

    def test_category_str_representation(self):
        """Test para la representación string de la categoría."""
        category = Category.objects.create(**self.category_data)
        self.assertEqual(str(category), "Camisetas")

    def test_category_unique_name(self):
        """Test para verificar que el nombre de categoría sea único."""
        Category.objects.create(**self.category_data)
        with self.assertRaises(IntegrityError):
            Category.objects.create(**self.category_data)

    def test_active_products_count(self):
        """Test para contar productos activos en una categoría."""
        category = Category.objects.create(**self.category_data)

        # Crear productos activos
        Product.objects.create(
            name="Camiseta Roja",
            sku="CAM-2T-RED-TEST1",
            category=category,
            size="2T",
            color="RED",
            price=Decimal("150.00"),
            stock=10,
            is_active=True,
        )

        Product.objects.create(
            name="Camiseta Azul",
            sku="CAM-3T-BLU-TEST2",
            category=category,
            size="3T",
            color="BLUE",
            price=Decimal("160.00"),
            stock=5,
            is_active=True,
        )

        # Crear producto inactivo
        Product.objects.create(
            name="Camiseta Verde",
            sku="CAM-4T-GRE-TEST3",
            category=category,
            size="4T",
            color="GREEN",
            price=Decimal("170.00"),
            stock=3,
            is_active=False,
        )

        self.assertEqual(category.active_products_count, 2)

    def test_soft_delete(self):
        """Test para verificar el soft delete."""
        category = Category.objects.create(**self.category_data)
        category_id = category.id

        # Soft delete
        category.delete()

        # Verificar que está marcado como eliminado
        category.refresh_from_db()
        self.assertTrue(category.is_deleted)
        self.assertIsNotNone(category.deleted_at)

        # Verificar que no aparece en consultas normales
        self.assertFalse(
            Category.objects.filter(id=category_id, is_deleted=False).exists()
        )


class ProductModelTest(TestCase):
    """Tests para el modelo Product."""

    def setUp(self):
        """Configuración inicial para los tests."""
        self.category = Category.objects.create(
            name="Pantalones", description="Pantalones para niños"
        )

        self.product_data = {
            "name": "Pantalón Azul",
            "category": self.category,
            "size": "3T",
            "color": "BLUE",
            "price": Decimal("200.00"),
            "cost": Decimal("120.00"),
            "stock": 15,
            "min_stock": 5,
            "description": "Pantalón cómodo para niños",
            "is_active": True,
        }

    def test_create_product(self):
        """Test para crear un producto."""
        product = Product.objects.create(**self.product_data)
        self.assertEqual(product.name, "Pantalón Azul")
        self.assertEqual(product.category, self.category)
        self.assertEqual(product.size, "3T")
        self.assertEqual(product.color, "BLUE")
        self.assertEqual(product.price, Decimal("200.00"))
        self.assertEqual(product.stock, 15)
        self.assertTrue(product.is_active)

    def test_sku_generation(self):
        """Test para verificar la generación automática del SKU."""
        product = Product.objects.create(**self.product_data)
        self.assertIsNotNone(product.sku)
        # El SKU debe tener el formato: CATEGORIA-TALLA-COLOR-UUID
        # Para 'Pantalones', '3T', 'BLUE' sería: PAN-3-BLU-XXXXXXXX
        self.assertTrue(product.sku.startswith("PAN-3-BLU"))
        # 4 partes separadas por guiones
        self.assertEqual(len(product.sku.split("-")), 4)

    def test_product_str_representation(self):
        """Test para la representación string del producto."""
        product = Product.objects.create(**self.product_data)
        expected_str = (
            f"{product.name} - "
            f"{product.get_size_display()} - "
            f"{product.get_color_display()}"
        )
        self.assertEqual(str(product), expected_str)

    def test_is_low_stock_property(self):
        """Test para la propiedad is_low_stock."""
        # Producto con stock normal
        product = Product.objects.create(**self.product_data)
        self.assertFalse(product.is_low_stock)

        # Producto con stock bajo
        product.stock = 3
        product.save()
        self.assertTrue(product.is_low_stock)

        # Producto con stock igual al mínimo
        product.stock = 5
        product.save()
        self.assertTrue(product.is_low_stock)

    def test_is_out_of_stock_property(self):
        """Test para la propiedad is_out_of_stock."""
        product = Product.objects.create(**self.product_data)
        self.assertFalse(product.is_out_of_stock)

        # Producto agotado
        product.stock = 0
        product.save()
        self.assertTrue(product.is_out_of_stock)

    def test_profit_margin_calculation(self):
        """Test para el cálculo del margen de ganancia."""
        product = Product.objects.create(**self.product_data)
        # Margen esperado: ((200 - 120) / 120) * 100 = 66.67%
        price = Decimal("200.00")
        cost = Decimal("120.00")
        expected_margin = ((price - cost) / cost) * 100
        self.assertAlmostEqual(
            float(product.profit_margin), float(expected_margin), places=2
        )

        # Producto sin costo
        product.cost = None
        product.save()
        self.assertIsNone(product.profit_margin)

    def test_update_stock_add(self):
        """Test para agregar stock."""
        product = Product.objects.create(**self.product_data)
        initial_stock = product.stock

        result = product.update_stock(10, "add")
        self.assertTrue(result)
        self.assertEqual(product.stock, initial_stock + 10)

    def test_update_stock_subtract(self):
        """Test para quitar stock."""
        product = Product.objects.create(**self.product_data)
        initial_stock = product.stock

        # Quitar stock válido
        result = product.update_stock(5, "subtract")
        self.assertTrue(result)
        self.assertEqual(product.stock, initial_stock - 5)

        # Intentar quitar más stock del disponible
        result = product.update_stock(20, "subtract")
        self.assertFalse(result)
        self.assertEqual(product.stock, initial_stock - 5)  # No debe cambiar

    def test_get_stock_status(self):
        """Test para obtener el estado del stock."""
        product = Product.objects.create(**self.product_data)

        # Stock normal
        self.assertEqual(product.get_stock_status(), "Disponible")

        # Stock bajo
        product.stock = 3
        product.save()
        self.assertEqual(product.get_stock_status(), "Stock Bajo")

        # Stock agotado
        product.stock = 0
        product.save()
        self.assertEqual(product.get_stock_status(), "Agotado")

    def test_get_stock_status_color(self):
        """Test para obtener el color del estado del stock."""
        product = Product.objects.create(**self.product_data)

        # Stock normal
        self.assertEqual(product.get_stock_status_color(), "green")

        # Stock bajo
        product.stock = 3
        product.save()
        self.assertEqual(product.get_stock_status_color(), "orange")

        # Stock agotado
        product.stock = 0
        product.save()
        self.assertEqual(product.get_stock_status_color(), "red")

    def test_unique_sku(self):
        """Test para verificar que el SKU sea único."""
        product1 = Product.objects.create(**self.product_data)

        # Intentar crear otro producto con el mismo SKU
        product_data_2 = self.product_data.copy()
        product_data_2["name"] = "Otro Pantalón"
        product_data_2["sku"] = product1.sku

        with self.assertRaises(IntegrityError):
            Product.objects.create(**product_data_2)


class ProductImageModelTest(TestCase):
    """Tests para el modelo ProductImage."""

    def setUp(self):
        """Configuración inicial para los tests."""
        self.category = Category.objects.create(
            name="Vestidos", description="Vestidos para niñas"
        )

        self.product = Product.objects.create(
            name="Vestido Rosa",
            category=self.category,
            size="4T",
            color="PINK",
            price=Decimal("250.00"),
            stock=8,
        )

    def create_test_image(self):
        """Crea una imagen de prueba."""
        image = Image.new("RGB", (100, 100), color="red")
        image_file = io.BytesIO()
        image.save(image_file, format="JPEG")
        image_file.seek(0)
        return SimpleUploadedFile(
            "test_image.jpg", image_file.getvalue(), content_type="image/jpeg"
        )

    def test_create_product_image(self):
        """Test para crear una imagen de producto."""
        test_image = self.create_test_image()

        product_image = ProductImage.objects.create(
            product=self.product, image=test_image, alt_text="Imagen de prueba", order=1
        )

        self.assertEqual(product_image.product, self.product)
        self.assertEqual(product_image.alt_text, "Imagen de prueba")
        self.assertEqual(product_image.order, 1)
        self.assertIsNotNone(product_image.image)

    def test_product_image_str_representation(self):
        """Test para la representación string de ProductImage."""
        test_image = self.create_test_image()

        product_image = ProductImage.objects.create(
            product=self.product, image=test_image
        )

        expected_str = f"Imagen de {self.product.name}"
        self.assertEqual(str(product_image), expected_str)

    def test_product_image_ordering(self):
        """Test para verificar el ordenamiento de las imágenes."""
        test_image1 = self.create_test_image()
        test_image2 = self.create_test_image()
        test_image3 = self.create_test_image()

        # Crear imágenes con diferentes órdenes
        img3 = ProductImage.objects.create(
            product=self.product, image=test_image3, order=3
        )

        img1 = ProductImage.objects.create(
            product=self.product, image=test_image1, order=1
        )

        img2 = ProductImage.objects.create(
            product=self.product, image=test_image2, order=2
        )

        # Verificar que se ordenan correctamente
        images = list(ProductImage.objects.filter(product=self.product))
        self.assertEqual(images[0], img1)
        self.assertEqual(images[1], img2)
        self.assertEqual(images[2], img3)

# Generated by Django 4.2.7 on 2025-06-22 23:30

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(help_text='Nombre de la categoría (ej: Camisetas, Pantalones, Vestidos)', max_length=100, unique=True, verbose_name='Nombre')),
                ('description', models.TextField(blank=True, help_text='Descripción detallada de la categoría', verbose_name='Descripción')),
                ('slug', models.SlugField(blank=True, help_text='URL amigable generada automáticamente', max_length=120, unique=True, verbose_name='Slug')),
                ('is_active', models.BooleanField(default=True, help_text='Indica si la categoría está activa', verbose_name='Activa')),
            ],
            options={
                'verbose_name': 'Categoría',
                'verbose_name_plural': 'Categorías',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(help_text='Nombre descriptivo del producto', max_length=200, verbose_name='Nombre')),
                ('sku', models.CharField(help_text='Código único del producto (Stock Keeping Unit)', max_length=50, unique=True, verbose_name='SKU')),
                ('size', models.CharField(choices=[('0-3m', '0-3 meses'), ('3-6m', '3-6 meses'), ('6-9m', '6-9 meses'), ('9-12m', '9-12 meses'), ('12-18m', '12-18 meses'), ('18-24m', '18-24 meses'), ('2T', '2 años'), ('3T', '3 años'), ('4T', '4 años'), ('5T', '5 años'), ('6T', '6 años'), ('7T', '7 años'), ('8T', '8 años'), ('XS', 'Extra Pequeño'), ('S', 'Pequeño'), ('M', 'Mediano'), ('L', 'Grande'), ('XL', 'Extra Grande')], help_text='Talla del producto', max_length=10, verbose_name='Talla')),
                ('color', models.CharField(choices=[('RED', 'Rojo'), ('BLUE', 'Azul'), ('GREEN', 'Verde'), ('YELLOW', 'Amarillo'), ('PINK', 'Rosa'), ('PURPLE', 'Morado'), ('ORANGE', 'Naranja'), ('BLACK', 'Negro'), ('WHITE', 'Blanco'), ('GRAY', 'Gris'), ('BROWN', 'Café'), ('NAVY', 'Azul Marino'), ('BEIGE', 'Beige'), ('TURQUOISE', 'Turquesa'), ('CORAL', 'Coral'), ('MINT', 'Menta'), ('MULTICOLOR', 'Multicolor')], help_text='Color principal del producto', max_length=20, verbose_name='Color')),
                ('price', models.DecimalField(decimal_places=2, help_text='Precio de venta del producto en pesos mexicanos', max_digits=10, validators=[django.core.validators.MinValueValidator(0.01)], verbose_name='Precio')),
                ('cost', models.DecimalField(blank=True, decimal_places=2, help_text='Costo de adquisición del producto', max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Costo')),
                ('stock', models.PositiveIntegerField(default=0, help_text='Cantidad disponible en inventario', verbose_name='Stock')),
                ('min_stock', models.PositiveIntegerField(default=5, help_text='Cantidad mínima antes de requerir reabastecimiento', verbose_name='Stock Mínimo')),
                ('is_active', models.BooleanField(default=True, help_text='Indica si el producto está disponible para venta', verbose_name='Activo')),
                ('description', models.TextField(blank=True, help_text='Descripción detallada del producto', verbose_name='Descripción')),
                ('image', models.ImageField(blank=True, help_text='Imagen principal del producto', null=True, upload_to='products/images/', verbose_name='Imagen')),
                ('barcode', models.CharField(blank=True, help_text='Código de barras del producto', max_length=50, null=True, verbose_name='Código de Barras')),
                ('category', models.ForeignKey(help_text='Categoría a la que pertenece el producto', on_delete=django.db.models.deletion.PROTECT, related_name='products', to='products.category', verbose_name='Categoría')),
            ],
            options={
                'verbose_name': 'Producto',
                'verbose_name_plural': 'Productos',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('image', models.ImageField(upload_to='products/gallery/', verbose_name='Imagen')),
                ('alt_text', models.CharField(blank=True, help_text='Descripción de la imagen para accesibilidad', max_length=200, verbose_name='Texto Alternativo')),
                ('order', models.PositiveIntegerField(default=0, help_text='Orden de visualización de la imagen', verbose_name='Orden')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='additional_images', to='products.product', verbose_name='Producto')),
            ],
            options={
                'verbose_name': 'Imagen de Producto',
                'verbose_name_plural': 'Imágenes de Productos',
                'ordering': ['order', 'created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['sku'], name='products_pr_sku_ca0cdc_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['category', 'is_active'], name='products_pr_categor_50f5f1_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['size', 'color'], name='products_pr_size_6932ca_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['stock'], name='products_pr_stock_4d23d5_idx'),
        ),
    ]

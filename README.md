# SanPedrito - Sistema de Inventario para Tienda Infantil

## 📋 Descripción

Sistema de gestión de inventario desarrollado en Django para SanPedrito, una tienda especializada en ropa infantil. El sistema incluye una API REST completa, panel de administración Django y está preparado para futuras extensiones.

## 🚀 Características Principales

### ✅ Funcionalidades Implementadas

- **Gestión de Productos**: CRUD completo con validaciones
- **Categorización**: Sistema de categorías para organizar productos
- **Control de Stock**: Alertas de stock bajo y agotado
- **API REST**: Endpoints completos con filtros avanzados
- **Panel Admin**: Interfaz administrativa personalizada
- **Autenticación JWT**: Sistema de tokens para la API
- **Documentación API**: Swagger/OpenAPI integrado
- **Dockerización**: Configuración completa para desarrollo y producción

### 🔄 Funcionalidades Planificadas

- **Fase 1**: Carritos de compra y órdenes
- **Fase 2**: Dashboard analítico y gestión de proveedores
- **Fase 3**: Cache con Redis y sistema de notificaciones

## 🛠️ Stack Tecnológico

- **Backend**: Django 4.2+, Django REST Framework
- **Base de Datos**: PostgreSQL (SQLite para desarrollo)
- **Autenticación**: Simple JWT
- **Documentación**: drf-spectacular (Swagger)
- **Containerización**: Docker & Docker Compose
- **Cache**: Redis (preparado para futuro uso)

## 📁 Estructura del Proyecto

```
sp_admin/
├── core/                   # App principal con modelos base
├── products/              # Gestión de productos y categorías
├── api/                   # API REST endpoints
├── sp_admin/              # Configuración del proyecto
├── requirements.txt       # Dependencias Python
├── Dockerfile            # Configuración Docker
├── docker-compose.yml    # Orquestación de servicios
└── README.md            # Este archivo
```

## 🚀 Instalación y Configuración

### Opción 1: Desarrollo Local

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd sp_admin
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. **Ejecutar migraciones**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Crear superusuario**
```bash
python manage.py createsuperuser
```

7. **Ejecutar servidor de desarrollo**
```bash
python manage.py runserver
```

### Opción 2: Docker (Recomendado)

1. **Ejecutar con Docker Compose**
```bash
docker-compose up --build
```

2. **Ejecutar migraciones en contenedor**
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## 📊 Modelos de Datos

### Category (Categoría)
- `name`: Nombre único de la categoría
- `description`: Descripción detallada
- `slug`: URL amigable
- `is_active`: Estado activo/inactivo

### Product (Producto)
- `sku`: Código único del producto
- `name`: Nombre descriptivo
- `category`: Relación con categoría
- `size`: Talla (0-3m, 3-6m, S, M, L, etc.)
- `color`: Color del producto
- `price`: Precio de venta
- `cost`: Costo de adquisición
- `stock`: Cantidad en inventario
- `min_stock`: Stock mínimo para alertas
- `is_active`: Estado activo/inactivo
- `image`: Imagen principal
- `barcode`: Código de barras

## 🔌 API Endpoints

### Autenticación
- `POST /api/v1/auth/token/` - Obtener token JWT
- `POST /api/v1/auth/token/refresh/` - Renovar token
- `POST /api/v1/auth/token/verify/` - Verificar token

### Categorías
- `GET /api/v1/categories/` - Listar categorías
- `POST /api/v1/categories/` - Crear categoría
- `GET /api/v1/categories/{slug}/` - Detalle de categoría
- `PUT/PATCH /api/v1/categories/{slug}/` - Actualizar categoría
- `DELETE /api/v1/categories/{slug}/` - Eliminar categoría

### Productos
- `GET /api/v1/products/` - Listar productos (con filtros)
- `POST /api/v1/products/` - Crear producto
- `GET /api/v1/products/{sku}/` - Detalle de producto
- `PUT/PATCH /api/v1/products/{sku}/` - Actualizar producto
- `DELETE /api/v1/products/{sku}/` - Eliminar producto

### Gestión de Stock
- `PATCH /api/v1/products/{sku}/update-stock/` - Actualizar stock
- `PATCH /api/v1/products/bulk-update/` - Actualización masiva

### Consultas Especiales
- `GET /api/v1/products/alerts/low-stock/` - Productos con stock bajo
- `GET /api/v1/products/alerts/out-of-stock/` - Productos agotados
- `GET /api/v1/inventory/stats/` - Estadísticas del inventario
- `GET /api/v1/search/products/` - Búsqueda avanzada

## 🔍 Filtros Disponibles

### Productos
- `category`: Filtrar por categoría
- `size`: Filtrar por talla
- `color`: Filtrar por color
- `min_price` / `max_price`: Rango de precios
- `in_stock`: Solo productos con stock
- `low_stock`: Solo productos con stock bajo
- `search`: Búsqueda en nombre, SKU, descripción

### Ejemplo de uso:
```
GET /api/v1/products/?category=1&size=S&color=RED&in_stock=true
```

## 🔐 Autenticación y Permisos

### Niveles de Acceso
- **Lectura Pública**: Categorías y productos (GET)
- **Escritura Autenticada**: Crear/actualizar productos (POST/PUT/PATCH)
- **Administración**: Eliminar productos (DELETE)

### Uso de JWT
```bash
# Obtener token
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Usar token en requests
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/products/
```

## 📖 Documentación de la API

La documentación interactiva está disponible en:
- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`
- **Schema JSON**: `http://localhost:8000/api/schema/`

## 🎛️ Panel de Administración

Accede al panel de administración en: `http://localhost:8000/admin/`

### Características del Admin
- **Búsqueda avanzada** por SKU, nombre, categoría
- **Filtros múltiples** por estado, stock, fecha
- **Acciones masivas** para activar/desactivar productos
- **Vista previa de imágenes**
- **Indicadores visuales** de stock bajo/agotado
- **Validaciones en tiempo real**

## 🧪 Testing

```bash
# Ejecutar tests
python manage.py test

# Con coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 🚀 Despliegue en Producción

### Variables de Entorno Requeridas
```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=sanpedrito_prod
DB_USER=prod_user
DB_PASSWORD=secure_password
DB_HOST=db_host
DB_PORT=5432
```

### Con Docker Compose (Producción)
```bash
docker-compose --profile production up -d
```

## 📈 Roadmap de Desarrollo

### Fase 1: E-commerce Básico (Próximo)
- [ ] Modelo de Carrito de Compras
- [ ] Sistema de Órdenes
- [ ] Estados de órdenes (Pendiente, Completado, Cancelado)
- [ ] Integración de pagos básica

### Fase 2: Analytics y Proveedores
- [ ] Dashboard con métricas de ventas
- [ ] Reportes de productos más vendidos
- [ ] Gestión de proveedores
- [ ] Órdenes de compra
- [ ] Alertas automáticas de restock

### Fase 3: Optimizaciones Avanzadas
- [ ] Cache con Redis
- [ ] Búsqueda con Elasticsearch
- [ ] Notificaciones push
- [ ] API de webhooks
- [ ] Integración con sistemas externos

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 📞 Soporte

Para soporte técnico o preguntas:
- Crear un issue en GitHub
- Contactar al equipo de desarrollo

## 🙏 Agradecimientos

- Django y Django REST Framework por el excelente framework
- La comunidad de Python por las librerías utilizadas
- Todos los contribuidores del proyecto

---

**SanPedrito Inventory Management System** - Desarrollado con ❤️ para la gestión eficiente de inventarios de tiendas infantiles.
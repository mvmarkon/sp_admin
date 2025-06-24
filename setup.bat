@echo off
echo ========================================
echo    SanPedrito - Setup del Proyecto
echo ========================================
echo.

echo 1. Instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error instalando dependencias
    pause
    exit /b 1
)

echo.
echo 2. Creando migraciones...
python manage.py makemigrations
if %errorlevel% neq 0 (
    echo Error creando migraciones
    pause
    exit /b 1
)

echo.
echo 3. Aplicando migraciones...
python manage.py migrate
if %errorlevel% neq 0 (
    echo Error aplicando migraciones
    pause
    exit /b 1
)

echo.
echo 4. Recopilando archivos estaticos...
python manage.py collectstatic --noinput
if %errorlevel% neq 0 (
    echo Error recopilando archivos estaticos
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Setup completado exitosamente!
echo ========================================
echo.
echo Proximos pasos:
echo 1. Crear superusuario: python manage.py createsuperuser
echo 2. Ejecutar servidor: python manage.py runserver
echo 3. Acceder a admin: http://localhost:8000/admin/
echo 4. Ver API docs: http://localhost:8000/api/docs/
echo.
pause
# SanPedrito - Script de Setup para PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    SanPedrito - Setup del Proyecto" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Función para verificar si un comando fue exitoso
function Test-Command {
    param($Description, $Command)
    
    Write-Host "$Description..." -ForegroundColor Yellow
    
    try {
        Invoke-Expression $Command
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $Description completado" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Error en: $Description" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Excepción en: $Description - $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Verificar si Python está instalado
Write-Host "Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python no encontrado. Por favor instala Python 3.10+" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Pasos del setup
$steps = @(
    @{Description="Instalando dependencias"; Command="pip install -r requirements.txt"},
    @{Description="Verificando configuración"; Command="python test_setup.py"},
    @{Description="Creando migraciones"; Command="python manage.py makemigrations"},
    @{Description="Aplicando migraciones"; Command="python manage.py migrate"},
    @{Description="Recopilando archivos estáticos"; Command="python manage.py collectstatic --noinput"}
)

$success = $true

foreach ($step in $steps) {
    $result = Test-Command -Description $step.Description -Command $step.Command
    if (-not $result) {
        $success = $false
        break
    }
    Write-Host ""
}

if ($success) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "    Setup completado exitosamente!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 Próximos pasos:" -ForegroundColor Cyan
    Write-Host "1. Crear superusuario: python manage.py createsuperuser" -ForegroundColor White
    Write-Host "2. Ejecutar servidor: python manage.py runserver" -ForegroundColor White
    Write-Host "3. Acceder a admin: http://localhost:8000/admin/" -ForegroundColor White
    Write-Host "4. Ver API docs: http://localhost:8000/api/docs/" -ForegroundColor White
    Write-Host ""
    Write-Host "🚀 Para desarrollo con Docker:" -ForegroundColor Cyan
    Write-Host "docker-compose up --build" -ForegroundColor White
} else {
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "    Setup falló. Revisa los errores." -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
}

Write-Host ""
Write-Host "Presiona cualquier tecla para continuar..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
#!/usr/bin/env python
"""
Script de prueba para verificar la configuración de Django.
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

def test_django_setup():
    """Prueba la configuración básica de Django."""
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sp_admin.settings')
    
    try:
        django.setup()
        print("✅ Django configurado correctamente")
        
        # Verificar apps instaladas
        installed_apps = settings.INSTALLED_APPS
        required_apps = ['core', 'products', 'api', 'rest_framework']
        
        for app in required_apps:
            if app in installed_apps:
                print(f"✅ App '{app}' encontrada")
            else:
                print(f"❌ App '{app}' no encontrada")
        
        # Verificar configuración de base de datos
        db_config = settings.DATABASES['default']
        print(f"✅ Base de datos configurada: {db_config['ENGINE']}")
        
        # Verificar configuración de REST Framework
        if hasattr(settings, 'REST_FRAMEWORK'):
            print("✅ Django REST Framework configurado")
        else:
            print("❌ Django REST Framework no configurado")
        
        print("\n🎉 Configuración básica verificada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en la configuración: {e}")
        return False

def test_models():
    """Prueba la importación de modelos."""
    try:
        from products.models import Category, Product
        from core.models import BaseModel
        
        print("✅ Modelos importados correctamente")
        print(f"  - Category: {Category}")
        print(f"  - Product: {Product}")
        print(f"  - BaseModel: {BaseModel}")
        
        return True
    except Exception as e:
        print(f"❌ Error importando modelos: {e}")
        return False

def test_serializers():
    """Prueba la importación de serializadores."""
    try:
        from api.serializers import ProductSerializer, CategorySerializer
        
        print("✅ Serializadores importados correctamente")
        print(f"  - ProductSerializer: {ProductSerializer}")
        print(f"  - CategorySerializer: {CategorySerializer}")
        
        return True
    except Exception as e:
        print(f"❌ Error importando serializadores: {e}")
        return False

def main():
    """Función principal de pruebas."""
    print("🔍 Iniciando verificación del setup de SanPedrito...\n")
    
    tests = [
        ("Configuración de Django", test_django_setup),
        ("Modelos", test_models),
        ("Serializadores", test_serializers),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Probando: {test_name}")
        print("-" * 40)
        result = test_func()
        results.append((test_name, result))
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{len(results)} pruebas pasaron")
    
    if passed == len(results):
        print("\n🎉 ¡Todas las pruebas pasaron! El setup está listo.")
        print("\n📝 Próximos pasos:")
        print("1. Ejecutar: python manage.py makemigrations")
        print("2. Ejecutar: python manage.py migrate")
        print("3. Ejecutar: python manage.py createsuperuser")
        print("4. Ejecutar: python manage.py runserver")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa la configuración.")
    
    return passed == len(results)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Script de diagnóstico para verificar las importaciones
"""

import sys
import os
from pathlib import Path

print("=== DIAGNÓSTICO DE IMPORTACIONES ===")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Script location: {__file__}")

# Verificar la ubicación del script
script_path = Path(__file__).resolve()
project_root = script_path.parent
print(f"Project root: {project_root}")

print("\nContenido de la carpeta raíz:")
for item in project_root.iterdir():
    print(f"  {item.name} {'(dir)' if item.is_dir() else '(file)'}")

print(f"\nSys.path actual:")
for i, path in enumerate(sys.path):
    print(f"  {i}: {path}")

# Agregar project root a sys.path si no está
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    print(f"\nAgregado {project_root} a sys.path")

# Verificar si las carpetas existen
frontend_path = project_root / "FrontEnd"
views_path = frontend_path / "Views"
styles_path = project_root / "Styles"

print(f"\nVerificación de carpetas:")
print(f"  FrontEnd exists: {frontend_path.exists()}")
print(f"  FrontEnd/Views exists: {views_path.exists()}")
print(f"  Styles exists: {styles_path.exists()}")

if frontend_path.exists():
    print(f"\nContenido de FrontEnd:")
    for item in frontend_path.iterdir():
        print(f"    {item.name}")

if views_path.exists():
    print(f"\nContenido de FrontEnd/Views:")
    for item in views_path.iterdir():
        print(f"    {item.name}")

# Verificar archivos __init__.py
init_files = [
    project_root / "__init__.py",
    frontend_path / "__init__.py", 
    views_path / "__init__.py",
    styles_path / "__init__.py"
]

print(f"\nArchivos __init__.py:")
for init_file in init_files:
    print(f"  {init_file}: {'EXISTS' if init_file.exists() else 'MISSING'}")

# Intentar las importaciones
print(f"\n=== INTENTANDO IMPORTACIONES ===")

try:
    print("Intentando: import FrontEnd")
    import FrontEnd
    print("  ✓ Éxito!")
except Exception as e:
    print(f"  ✗ Error: {e}")

try:
    print("Intentando: from FrontEnd.Views import report_tab")
    from FrontEnd.Views import report_tab
    print("  ✓ Éxito!")
except Exception as e:
    print(f"  ✗ Error: {e}")

try:
    print("Intentando: from FrontEnd.Views.report_tab import ReportTab")
    from FrontEnd.Views.report_tab import ReportTab
    print("  ✓ Éxito!")
except Exception as e:
    print(f"  ✗ Error: {e}")

print(f"\n=== FIN DEL DIAGNÓSTICO ===")
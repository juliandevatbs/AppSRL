#!/usr/bin/env python3
"""
Script de ejecución para la aplicación
Ejecutar desde la carpeta raíz del proyecto
"""

import sys
from pathlib import Path

# Agregar la carpeta raíz al path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# Importar y ejecutar la aplicación principal
from FrontEnd.main_gui import main

if __name__ == "__main__":
    main()
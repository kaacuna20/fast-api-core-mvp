"""
Script de acceso rápido para ejecutar seeders
Uso:
    python seed.py create <nombre>    # Crear un nuevo seeder
    python seed.py run                # Ejecutar todos los seeders
    python seed.py run <nombre>       # Ejecutar un seeder específico
"""

import sys
from database.seeders_command import main

if __name__ == '__main__':
    main()

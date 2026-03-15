"""
Sistema de Seeders para FastAPI
Comandos disponibles:
    - python database/seeders_command.py create <nombre>  : Crear un nuevo seeder
    - python database/seeders_command.py run              : Ejecutar todos los seeders
    - python database/seeders_command.py run <nombre>     : Ejecutar un seeder específico
"""

import os
import sys
import argparse
import importlib
from pathlib import Path
from datetime import datetime
from typing import List, Type

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.core import SessionLocal
from sqlalchemy.orm import Session


class BaseSeeder:
    """Clase base para los seeders. Proporciona acceso a la base de datos y métodos comunes."""
    
    def __init__(self, db: Session = None):
        """
        Inicializa el seeder con una sesión de base de datos.
        
        Args:
            db: Sesión de SQLAlchemy. Si no se proporciona, se crea una nueva.
        """
        self.db = db or SessionLocal()
        self._should_close_db = db is None
    
    def run(self):
        """Método que debe ser implementado por cada seeder para ejecutar la lógica de inserción de datos."""
        raise NotImplementedError(
            f"El método run() debe ser implementado en {self.__class__.__name__}"
        )
    
    def execute(self):
        """Ejecuta el seeder y maneja la sesión de base de datos."""
        try:
            print(f"🌱 Ejecutando seeder: {self.__class__.__name__}")
            self.run()
            self.db.commit()
            print(f"✅ Seeder {self.__class__.__name__} ejecutado exitosamente")
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error en seeder {self.__class__.__name__}: {str(e)}")
            raise
        finally:
            if self._should_close_db:
                self.db.close()
    
    def truncate(self, model):
        """Elimina todos los registros de una tabla."""
        try:
            self.db.query(model).delete()
            self.db.commit()
            print(f"🗑️  Tabla {model.__tablename__} truncada")
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error al truncar tabla {model.__tablename__}: {str(e)}")
            raise


class SeederManager:
    """Gestor de seeders. Se encarga de descubrir, cargar y ejecutar seeders."""
    
    def __init__(self):
        self.seeders_dir = Path(__file__).parent / "seeders"
        self.seeders_dir.mkdir(exist_ok=True)
    
    def get_seeder_files(self) -> List[str]:
        """Obtiene la lista de archivos de seeders en la carpeta seeders."""
        files = []
        for file in self.seeders_dir.glob("*.py"):
            if file.name != "__init__.py" and not file.name.startswith("_"):
                files.append(file.stem)
        return sorted(files)
    
    def load_seeder_class(self, seeder_name: str) -> Type[BaseSeeder]:
        """Carga dinámicamente una clase de seeder desde su archivo."""
        try:
            # Importar el módulo del seeder
            module_name = f"database.seeders.{seeder_name}"
            module = importlib.import_module(module_name)
            
            # Buscar la clase que hereda de BaseSeeder
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BaseSeeder) and 
                    attr is not BaseSeeder):
                    return attr
            
            raise ValueError(f"No se encontró una clase que herede de BaseSeeder en {seeder_name}.py")
        except ImportError as e:
            raise ImportError(f"No se pudo importar el seeder {seeder_name}: {str(e)}")
    
    def run_seeder(self, seeder_name: str, db: Session = None):
        """Ejecuta un seeder específico."""
        seeder_class = self.load_seeder_class(seeder_name)
        seeder = seeder_class(db=db)
        seeder.execute()
    
    def run_all_seeders(self):
        """Ejecuta todos los seeders en orden alfabético."""
        seeder_files = self.get_seeder_files()
        
        if not seeder_files:
            print("⚠️  No se encontraron seeders para ejecutar")
            return
        
        print(f"🌱 Ejecutando {len(seeder_files)} seeder(s)...\n")
        
        db = SessionLocal()
        try:
            for seeder_name in seeder_files:
                try:
                    self.run_seeder(seeder_name, db=db)
                except Exception as e:
                    print(f"❌ Error al ejecutar {seeder_name}: {str(e)}")
                    if input("\n¿Continuar con los siguientes seeders? (s/n): ").lower() != 's':
                        break
                print()  # Línea en blanco entre seeders
            
            print("✅ Proceso de seeding completado")
        finally:
            db.close()
    
    def create_seeder(self, seeder_name: str):
        """Crea un nuevo archivo de seeder con un template base."""
        # Convertir el nombre a formato de clase (PascalCase)
        class_name = ''.join(word.capitalize() for word in seeder_name.split('_'))
        if not class_name.endswith('Seeder'):
            class_name += 'Seeder'
        
        # Nombre del archivo (snake_case)
        file_name = seeder_name.lower()
        if not file_name.endswith('_seeder'):
            file_name += '_seeder'
        
        file_path = self.seeders_dir / f"{file_name}.py"
        
        # Verificar si el archivo ya existe
        if file_path.exists():
            print(f"❌ El seeder {file_name}.py ya existe")
            return
        
        # Template del seeder
        template = f'''"""
        Seeder: {class_name}
        Creado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """

        from database.seeders_command import BaseSeeder
        # from models import User, Role  # Importar los modelos que necesites


        class {class_name}(BaseSeeder):
            """Seeder para poblar datos de ejemplo."""
            
            def run(self):
                """Ejecuta el seeder."""
                # Ejemplo: Crear registros
                # self.truncate(User)  # Opcional: limpiar la tabla primero
                
                # Crear datos usando el modelo
                # users_data = [
                #     {{"email": "user1@example.com", "password": "password123"}},
                #     {{"email": "user2@example.com", "password": "password123"}},
                # ]
                # 
                # for data in users_data:
                #     user = User(**data)
                #     self.db.add(user)
                
                print("    ℹ️  Implementa la lógica del seeder en el método run()")
                pass
        '''
        
        # Crear el archivo
        file_path.write_text(template, encoding='utf-8')
        print(f"✅ Seeder creado: {file_path}")
        print(f"📝 Clase: {class_name}")
        print(f"\nPara ejecutarlo:")
        print(f"    python database/seeders_command.py run {file_name}")


def main():
    parser = argparse.ArgumentParser(
        description='Sistema de Seeders para FastAPI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
    # Crear un nuevo seeder
    python database/seeders_command.py create users
    python database/seeders_command.py create roles_and_permissions
    
    # Ejecutar todos los seeders
    python database/seeders_command.py run
    
    # Ejecutar un seeder específico
    python database/seeders_command.py run users_seeder
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando: create
    create_parser = subparsers.add_parser('create', help='Crear un nuevo seeder')
    create_parser.add_argument('name', type=str, help='Nombre del seeder (ej: users, roles)')
    
    # Comando: run
    run_parser = subparsers.add_parser('run', help='Ejecutar seeders')
    run_parser.add_argument(
        'seeder',
        type=str,
        nargs='?',
        help='Nombre del seeder a ejecutar (opcional, por defecto ejecuta todos)'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = SeederManager()
    
    if args.command == 'create':
        manager.create_seeder(args.name)
    
    elif args.command == 'run':
        if args.seeder:
            # Ejecutar un seeder específico
            try:
                manager.run_seeder(args.seeder)
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                sys.exit(1)
        else:
            # Ejecutar todos los seeders
            manager.run_all_seeders()


if __name__ == '__main__':
    main()
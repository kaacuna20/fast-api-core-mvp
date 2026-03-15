# Sistema de Seeders

Sistema completo para crear y ejecutar seeders en la aplicación FastAPI.

## 📋 Características

- ✅ Crear nuevos seeders con plantillas base
- ✅ Ejecutar todos los seeders o uno específico
- ✅ Acceso directo a la base de datos mediante `self.db`
- ✅ Método `truncate()` para limpiar tablas
- ✅ Manejo automático de transacciones y errores
- ✅ Uso de modelos que heredan de `BaseModel`

## 🚀 Comandos

### Crear un nuevo seeder

```bash
# Desde la carpeta fast/
python database/seeders_command.py create nombre_del_seeder
```

Ejemplos:
```bash
python database/seeders_command.py create roles
python database/seeders_command.py create users
python database/seeders_command.py create products
```

### Ejecutar seeders

```bash
# Ejecutar todos los seeders (en orden alfabético)
python database/seeders_command.py run

# Ejecutar un seeder específico
python database/seeders_command.py run roles_seeder
python database/seeders_command.py run users_seeder
```

## 📝 Estructura de un Seeder

Un seeder es una clase que hereda de `BaseSeeder` e implementa el método `run()`:

```python
from database.seeders_command import BaseSeeder
from models import User, Role


class UsersSeeder(BaseSeeder):
    """Descripción del seeder."""
    
    def run(self):
        """Ejecuta el seeder."""
        # 1. Opcional: Limpiar la tabla
        # self.truncate(User)
        
        # 2. Verificar datos existentes
        if self.db.query(User).count() > 0:
            print("    ℹ️  Ya existen usuarios. Saltando...")
            return
        
        # 3. Crear datos
        users_data = [
            {"email": "user1@example.com", "password": "pass123"},
            {"email": "user2@example.com", "password": "pass123"},
        ]
        
        for data in users_data:
            user = User(**data)
            self.db.add(user)
        
        print(f"    ✅ {len(users_data)} usuarios creados")
```

## 🔧 Métodos Disponibles

### `self.db`
Sesión de SQLAlchemy para interactuar con la base de datos.

```python
# Crear un registro
user = User(email="test@example.com", password="123")
self.db.add(user)

# Consultar registros
admin_role = self.db.query(Role).filter(Role.reference == "admin").first()

# Contar registros
count = self.db.query(User).count()
```

### `self.truncate(Model)`
Elimina todos los registros de una tabla.

```python
self.truncate(User)  # Elimina todos los usuarios
self.truncate(Role)  # Elimina todos los roles
```

## 📁 Ejemplos Incluidos

### `roles_seeder.py`
Crea roles básicos del sistema (admin, user, guest).

### `users_seeder.py`
Crea usuarios de ejemplo con roles asignados.

## 🎯 Buenas Prácticas

1. **Nombres**: Usa snake_case para nombres de archivo: `users_seeder.py`, `categories_seeder.py`

2. **Orden**: Los seeders se ejecutan en orden alfabético. Si hay dependencias:
   - `01_roles_seeder.py`
   - `02_users_seeder.py`
   - `03_products_seeder.py`

3. **Idempotencia**: Verifica si los datos ya existen antes de crearlos:
   ```python
   if self.db.query(Model).count() > 0:
       print("    ℹ️  Datos ya existen. Saltando...")
       return
   ```

4. **Seguridad**: En producción, hashea las contraseñas:
   ```python
   from passlib.hash import bcrypt
   
   user = User(
       email="admin@example.com",
       password=bcrypt.hash("password123")
   )
   ```

5. **Mensajes**: Usa mensajes claros para indicar progreso:
   ```python
   print(f"    ✅ {len(data)} registros creados")
   print(f"    ℹ️  Información importante")
   print(f"    ⚠️  Advertencia")
   ```

## 🔄 Flujo de Trabajo

1. **Crear el seeder**:
   ```bash
   python database/seeders_command.py create products
   ```

2. **Editar el archivo** generado en `database/seeders/products_seeder.py`

3. **Implementar la lógica** en el método `run()`

4. **Ejecutar el seeder**:
   ```bash
   python database/seeders_command.py run products_seeder
   ```

## ⚠️ Notas Importantes

- Los seeders se ejecutan **dentro de una transacción**
- Si hay un error, se hace **rollback automático**
- Usa `self.db.commit()` solo si necesitas commits parciales (no recomendado)
- El commit final se hace automáticamente al terminar `run()`

## 🐛 Troubleshooting

**Error: "No se encontró una clase que herede de BaseSeeder"**
- Asegúrate de que tu clase hereda de `BaseSeeder`
- Verifica que el nombre de la clase termine en `Seeder`

**Error: "No se pudo importar el seeder"**
- Verifica que el archivo esté en `database/seeders/`
- Revisa errores de sintaxis en el archivo del seeder

**Los datos no se guardan**
- Asegúrate de hacer `self.db.add(instance)` para cada registro
- El commit se hace automáticamente, no lo hagas manual

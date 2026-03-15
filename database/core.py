from datetime import datetime
from typing import List, Optional, Any
from sqlalchemy import Column, DateTime, event, select
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from config.db_conection import Database
from config.settings import Settings



database = Database(settings=Settings())
Base = database.Base
SessionLocal = database.SessionLocal

class QueryManager:
    """Manager estilo Django para hacer queries más simples"""
    
    def __init__(self, model_class, session=None, filters=None, order_clauses=None):
        self.model_class = model_class
        self.external_session = session  # Sesión externa si se proporciona
        self._filters = filters or []  # Lista de condiciones de filtro
        self._order_clauses = order_clauses or []  # Lista de ordenamientos
    
    def _execute_query(self, func):
        """Ejecuta una query manejando la sesión correctamente"""
        if self.external_session:
            # Si hay una sesión externa, usarla sin cerrarla
            return func(self.external_session)
        else:
            # Usar el método get_db de Database para manejar la sesión
            db_generator = database.get_db()
            session = next(db_generator)
            try:
                result = func(session)
                return result
            finally:
                try:
                    next(db_generator)
                except StopIteration:
                    pass
    
    def _build_statement(self):
        """Construye el statement con filtros y ordenamiento aplicados"""
        stmt = select(self.model_class)
        
        # Aplicar filtros
        for condition in self._filters:
            stmt = stmt.filter(condition)
        
        # Aplicar ordenamientos
        for order_clause in self._order_clauses:
            stmt = stmt.order_by(order_clause)
        
        return stmt
    
    def using(self, session):
        """Permite usar una sesión específica"""
        return QueryManager(
            self.model_class, 
            session=session, 
            filters=self._filters.copy(),
            order_clauses=self._order_clauses.copy()
        )
    
    def all(self) -> List[Any]:
        """Obtiene todos los registros"""
        def query(session):
            stmt = self._build_statement()
            result = session.execute(stmt)
            return result.scalars().all()
        return self._execute_query(query)
    
    def filter(self, *args, **kwargs):
        """Filtra registros por condiciones - retorna QueryManager para encadenar"""
        # Construir condiciones de filtro
        new_filters = self._filters.copy()
        
        # Aplicar filtros de kwargs
        for key, value in kwargs.items():
            if hasattr(self.model_class, key):
                new_filters.append(getattr(self.model_class, key) == value)
        
        # Aplicar filtros de args (expresiones SQLAlchemy)
        for condition in args:
            new_filters.append(condition)
        
        # Retornar nuevo QueryManager con filtros agregados
        return QueryManager(
            self.model_class,
            session=self.external_session,
            filters=new_filters,
            order_clauses=self._order_clauses.copy()
        )
    
    def order_by(self, *fields):
        """Ordena los resultados - retorna QueryManager para encadenar
        
        Ejemplos:
            User.objects.order_by('email')  # Ascendente
            User.objects.order_by('-created_at')  # Descendente (con -)
            User.objects.filter(is_active=True).order_by('name', '-created_at')
        """
        from sqlalchemy import desc, asc
        
        new_order_clauses = self._order_clauses.copy()
        
        for field in fields:
            if isinstance(field, str):
                # Si empieza con -, es orden descendente
                if field.startswith('-'):
                    field_name = field[1:]
                    if hasattr(self.model_class, field_name):
                        new_order_clauses.append(desc(getattr(self.model_class, field_name)))
                else:
                    field_name = field
                    if hasattr(self.model_class, field_name):
                        new_order_clauses.append(asc(getattr(self.model_class, field_name)))
            else:
                # Si es una expresión SQLAlchemy directamente
                new_order_clauses.append(field)
        
        # Retornar nuevo QueryManager con ordenamiento agregado
        return QueryManager(
            self.model_class,
            session=self.external_session,
            filters=self._filters.copy(),
            order_clauses=new_order_clauses
        )
    
    def get(self, *args, **kwargs) -> Optional[Any]:
        """Obtiene un único registro"""
        # Si se pasan argumentos, crear filtros y ejecutar
        if args or kwargs:
            query_manager = self.filter(*args, **kwargs)
            def query(session):
                stmt = query_manager._build_statement()
                result = session.execute(stmt)
                return result.scalar_one_or_none()
            return self._execute_query(query)
        
        # Si no hay argumentos, ejecutar con filtros existentes
        def query(session):
            stmt = self._build_statement()
            result = session.execute(stmt)
            return result.scalar_one_or_none()
        return self._execute_query(query)
    
    def first(self) -> Optional[Any]:
        """Obtiene el primer registro"""
        def query(session):
            stmt = self._build_statement().limit(1)
            result = session.execute(stmt)
            return result.scalar_one_or_none()
        return self._execute_query(query)
    
    def count(self) -> int:
        """Cuenta los registros"""
        def query(session):
            from sqlalchemy import func as sql_func
            stmt = select(sql_func.count()).select_from(self.model_class)
            
            # Aplicar filtros al count
            for condition in self._filters:
                stmt = stmt.filter(condition)
            
            result = session.execute(stmt)
            return result.scalar()
        return self._execute_query(query)
    
    def create(self, **kwargs) -> Any:
        """Crea un nuevo registro"""
        def query(session):
            instance = self.model_class(**kwargs)
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance
        return self._execute_query(query)
    
    def with_deleted(self):
        """Incluye registros eliminados (solo para SoftDeleteModel)"""
        return QueryManagerWithDeleted(
            self.model_class, 
            session=self.external_session,
            filters=self._filters.copy(),
            order_clauses=self._order_clauses.copy()
        )
    
    def to_dict(self, instance) -> dict:
        """Convierte una instancia a diccionario"""
        if not instance:
            return {}
        return {column.name: getattr(instance, column.name) for column in instance.__table__.columns}


class QueryManagerWithDeleted(QueryManager):
    """Manager que incluye registros eliminados"""
    
    def _build_statement(self):
        """Construye el statement con include_deleted=True"""
        stmt = select(self.model_class).execution_options(include_deleted=True)
        
        # Aplicar filtros
        for condition in self._filters:
            stmt = stmt.filter(condition)
        
        # Aplicar ordenamientos
        for order_clause in self._order_clauses:
            stmt = stmt.order_by(order_clause)
        
        return stmt


class ManagerDescriptor:
    """Descriptor para acceder al manager desde la clase del modelo"""
    
    def __get__(self, instance, owner):
        if instance is not None:
            # Si se accede desde una instancia, retornar None o error
            return None
        # Si se accede desde la clase, retornar el manager
        return QueryManager(owner, session=None, filters=[], order_clauses=[])


class BaseModel(Base):
    __abstract__ = True
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Manager estilo Django
    objects = ManagerDescriptor()
    
    def save(self):
        """Guarda o actualiza la instancia en la base de datos"""
        db_generator = database.get_db()
        session = next(db_generator)
        try:
            session.add(self)
            session.commit()
            session.refresh(self)
            return self
        except Exception as e:
            session.rollback()
            raise e
        finally:
            try:
                next(db_generator)
            except StopIteration:
                pass


class SoftDeleteModel(BaseModel):
    __abstract__ = True
    
    deleted_at = Column(DateTime, nullable=True)

    def delete(self):
        self.deleted_at = datetime.now()


# Evento para filtrar automáticamente registros con soft delete
@event.listens_for(Session, "do_orm_execute")
def _soft_delete_filter(execute_state):
    """
    Intercepta todas las queries SELECT y agrega filtro deleted_at IS NULL
    para modelos que hereden de SoftDeleteModel
    """
    if not execute_state.is_select:
        return
    
    # Verificar si hay un flag para incluir eliminados
    if execute_state.execution_options.get("include_deleted", False):
        return
    
    # Aplicar filtro a todas las entidades que tengan deleted_at
    for entity in execute_state.statement.column_descriptions:
        if entity.get("entity") is not None:
            mapper = entity["entity"]
            if hasattr(mapper, "deleted_at"):
                execute_state.statement = execute_state.statement.filter(
                    mapper.deleted_at.is_(None)
                )

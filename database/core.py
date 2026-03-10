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
    
    def __init__(self, model_class, session=None):
        self.model_class = model_class
        self.external_session = session  # Sesión externa si se proporciona
    
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
    
    def using(self, session):
        """Permite usar una sesión específica"""
        return QueryManager(self.model_class, session=session)
    
    def all(self) -> List[Any]:
        """Obtiene todos los registros"""
        def query(session):
            result = session.execute(select(self.model_class))
            return result.scalars().all()
        return self._execute_query(query)
    
    def filter(self, *args, **kwargs) -> List[Any]:
        """Filtra registros por condiciones"""
        def query(session):
            stmt = select(self.model_class)
            
            # Aplicar filtros de kwargs
            for key, value in kwargs.items():
                if hasattr(self.model_class, key):
                    stmt = stmt.filter(getattr(self.model_class, key) == value)
            
            # Aplicar filtros de args (expresiones SQLAlchemy)
            for condition in args:
                stmt = stmt.filter(condition)
            
            result = session.execute(stmt)
            return result.scalars().all()
        return self._execute_query(query)
    
    def get(self, *args, **kwargs) -> Optional[Any]:
        """Obtiene un único registro"""
        def query(session):
            stmt = select(self.model_class)
            
            # Aplicar filtros
            for key, value in kwargs.items():
                if hasattr(self.model_class, key):
                    stmt = stmt.filter(getattr(self.model_class, key) == value)
            
            for condition in args:
                stmt = stmt.filter(condition)
            
            result = session.execute(stmt)
            return result.scalar_one_or_none()
        return self._execute_query(query)
    
    def first(self) -> Optional[Any]:
        """Obtiene el primer registro"""
        def query(session):
            result = session.execute(select(self.model_class).limit(1))
            return result.scalar_one_or_none()
        return self._execute_query(query)
    
    def count(self) -> int:
        """Cuenta los registros"""
        def query(session):
            from sqlalchemy import func as sql_func
            result = session.execute(
                select(sql_func.count()).select_from(self.model_class)
            )
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
        return QueryManagerWithDeleted(self.model_class, session=self.external_session)


class QueryManagerWithDeleted(QueryManager):
    """Manager que incluye registros eliminados"""
    
    def all(self) -> List[Any]:
        def query(session):
            result = session.execute(
                select(self.model_class).execution_options(include_deleted=True)
            )
            return result.scalars().all()
        return self._execute_query(query)
    
    def filter(self, *args, **kwargs) -> List[Any]:
        def query(session):
            stmt = select(self.model_class).execution_options(include_deleted=True)
            
            for key, value in kwargs.items():
                if hasattr(self.model_class, key):
                    stmt = stmt.filter(getattr(self.model_class, key) == value)
            
            for condition in args:
                stmt = stmt.filter(condition)
            
            result = session.execute(stmt)
            return result.scalars().all()
        return self._execute_query(query)


class ManagerDescriptor:
    """Descriptor para acceder al manager desde la clase del modelo"""
    
    def __get__(self, instance, owner):
        if instance is not None:
            # Si se accede desde una instancia, retornar None o error
            return None
        # Si se accede desde la clase, retornar el manager
        return QueryManager(owner)


class BaseModel(Base):
    __abstract__ = True
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Manager estilo Django
    objects = ManagerDescriptor()


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

    

    
    




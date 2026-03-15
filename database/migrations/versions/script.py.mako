"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}

#cd fast

# 1. Crear una migración automática (detecta cambios en modelos)
#alembic revision --autogenerate -m "Initial migration"

# 2. Aplicar migraciones pendientes
#alembic upgrade head

# 3. Revertir última migración
#alembic downgrade -1

# 4. Ver historial de migraciones
#alembic history

# 5. Ver estado actual
#alembic current
"""Added ondelete settings

Revision ID: d66b7c647336
Revises: b933607d4b72
Create Date: 2025-01-26 12:17:04.817745

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd66b7c647336'
down_revision: Union[str, None] = 'b933607d4b72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('department_equipment_equipment_id_fkey', 'department_equipment', type_='foreignkey')
    op.drop_constraint('department_equipment_department_id_fkey', 'department_equipment', type_='foreignkey')
    op.create_foreign_key(None, 'department_equipment', 'equipment', ['equipment_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'department_equipment', 'departments', ['department_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('departments_factory_id_fkey', 'departments', type_='foreignkey')
    op.create_foreign_key(None, 'departments', 'factories', ['factory_id'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'departments', type_='foreignkey')
    op.create_foreign_key('departments_factory_id_fkey', 'departments', 'factories', ['factory_id'], ['id'])
    op.drop_constraint(None, 'department_equipment', type_='foreignkey')
    op.drop_constraint(None, 'department_equipment', type_='foreignkey')
    op.create_foreign_key('department_equipment_department_id_fkey', 'department_equipment', 'departments', ['department_id'], ['id'])
    op.create_foreign_key('department_equipment_equipment_id_fkey', 'department_equipment', 'equipment', ['equipment_id'], ['id'])
    # ### end Alembic commands ###

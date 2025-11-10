"""Add name and role to users

Revision ID: a77a48da9b6f
Revises: 268b4c53a0e7
Create Date: 2025-11-10 17:00:00.000000
"""

import sqlalchemy as sa

from alembic import op

# IDs de controlo do Alembic
revision = "a77a48da9b6f"
down_revision = "268b4c53a0e7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Adiciona coluna 'name'
    op.add_column(
        "users",
        sa.Column("name", sa.String(length=255), nullable=True),
    )

    # Adiciona coluna 'role' com default 'user'
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(length=50),
            nullable=False,
            server_default="user",
        ),
    )

    # Índice opcional para role (útil para dashboard/admin)
    op.create_index("ix_users_role", "users", ["role"])


def downgrade() -> None:
    # Reverte as alterações
    op.drop_index("ix_users_role", table_name="users")
    op.drop_column("users", "role")
    op.drop_column("users", "name")
    op.drop_column("users", "name")
    op.drop_column("users", "name")
    op.drop_column("users", "name")
    op.drop_column("users", "name")

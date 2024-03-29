"""empty message

Revision ID: 9f98c73ea81f
Revises: cea006e74b5c
Create Date: 2017-10-29 11:24:55.982847

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9f98c73ea81f"
down_revision = "cea006e74b5c"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint("_source_uid_uc", "event", ["source_id", "uid"])
    op.drop_constraint("event_uid_key", "event", type_="unique")
    op.alter_column(
        "user", "email", existing_type=sa.VARCHAR(length=120), nullable=True
    )
    op.alter_column(
        "user", "username", existing_type=sa.VARCHAR(length=80), nullable=True
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "user", "username", existing_type=sa.VARCHAR(length=80), nullable=False
    )
    op.alter_column(
        "user", "email", existing_type=sa.VARCHAR(length=120), nullable=False
    )
    op.create_unique_constraint("event_uid_key", "event", ["uid"])
    op.drop_constraint("_source_uid_uc", "event", type_="unique")
    # ### end Alembic commands ###

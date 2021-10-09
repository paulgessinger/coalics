"""reinit

Revision ID: fb179d4df2b5
Revises: e261a8586dc6
Create Date: 2020-06-10 20:03:09.040174

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fb179d4df2b5"
down_revision = "e261a8586dc6"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.String(length=255), nullable=True),
        sa.Column("data", sa.LargeBinary(), nullable=True),
        sa.Column("expiry", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("sessions")
    # ### end Alembic commands ###

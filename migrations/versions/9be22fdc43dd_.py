"""empty message

Revision ID: 9be22fdc43dd
Revises: fb179d4df2b5
Create Date: 2021-08-17 21:57:08.642701

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9be22fdc43dd"
down_revision = "fb179d4df2b5"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "calendar_source",
        sa.Column("all_day_override", sa.Boolean(), nullable=False, server_default="0"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("calendar_source", "all_day_override")
    # ### end Alembic commands ###

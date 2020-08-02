"""empty message

Revision ID: be66fc3090c4
Revises: 8ef1e37e40b9
Create Date: 2020-08-02 19:32:15.517381

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from coalics import User, db

revision = 'be66fc3090c4'
down_revision = '8ef1e37e40b9'
branch_labels = None
depends_on = None


def upgrade():
    users = User.query.all()
    for user in users:
      print(user)
      user.email = user.email
    db.session.commit()


def downgrade():
    raise NotImplementedError("I can't unhash the emails, sorry :/")

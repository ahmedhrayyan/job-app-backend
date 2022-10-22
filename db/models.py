import bcrypt
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
from db import db


class MutateMixin:
    """ Share common mutate methods with models """

    def update(self, **kwargs):
        """ update element in db  """

        # update fields using python dict
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def delete(self):
        """ delete item from db """
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def insert(self):
        """ insert item into db """
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e


class BaseMixin:
    """ Share common columns """
    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime(timezone=True), default=datetime.now(timezone.utc))


class Admin(MutateMixin, BaseMixin, db.Model):
    __tablename__ = "admins"
    email = sa.Column(sa.VARCHAR(64), nullable=False, unique=True)
    name = sa.Column(sa.String, nullable=False)
    _password = sa.Column(sa.LargeBinary, nullable=False)
    jobs = relationship("Job", cascade="all, delete")

    @property
    def password(self):
        return "***"

    @password.setter
    def password(self, value):
        self._password = bcrypt.hashpw(bytes(value, 'utf-8'), bcrypt.gensalt(12))

    def checkpw(self, password: str):
        """ Check if the provided password is equal to user password """
        return bcrypt.checkpw(bytes(password, 'utf-8'), self._password)


class Job(MutateMixin, BaseMixin, db.Model):
    __tablename__ = "jobs"
    admin_id = sa.Column(sa.Integer, sa.ForeignKey("admins.id"), nullable=False)
    title = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.Text, nullable=False)
    vacancy = sa.Column(sa.Integer, nullable=False)
    salary = sa.Column(sa.String, nullable=False)
    location = sa.Column(sa.String, nullable=False)
    type = sa.Column(sa.Integer, nullable=False)
    company_name = sa.Column(sa.String, nullable=False)
    company_logo = sa.Column(sa.String, nullable=False)
    company_email = sa.Column(sa.String, nullable=False)

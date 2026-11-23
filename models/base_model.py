#!/usr/bin/python3
"""Defines the BaseModel class, parent of all the AirBnB models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
import models

Base = declarative_base()


def _is_related(value):
    """Return True if value is a model or a list of models (a relationship)."""
    if isinstance(value, BaseModel):
        return True
    return (isinstance(value, list) and
            any(isinstance(item, BaseModel) for item in value))


class BaseModel:
    """Defines the attributes and methods common to all the models."""

    id = Column(String(60), primary_key=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, *args, **kwargs):
        """Create an instance, setting the attributes given in kwargs."""
        for key, value in kwargs.items():
            if key == "__class__":
                continue
            if key in ("created_at", "updated_at") and isinstance(value, str):
                value = datetime.fromisoformat(value)
            setattr(self, key, value)
        table = getattr(self, "__table__", None)
        if table is not None:
            for column in table.columns:
                default = column.default
                if (column.name not in kwargs and default is not None
                        and default.is_scalar):
                    setattr(self, column.name, default.arg)
        if "id" not in kwargs:
            self.id = str(uuid.uuid4())
        now = datetime.utcnow()
        if "created_at" not in kwargs:
            self.created_at = now
        if "updated_at" not in kwargs:
            self.updated_at = now

    def __str__(self):
        """Return the string [<class name>] (<id>) <attributes>."""
        data = dict(self.__dict__)
        data.pop("_sa_instance_state", None)
        return "[{}] ({}) {}".format(type(self).__name__, self.id, data)

    def save(self):
        """Update updated_at, add the instance to storage and save it."""
        self.updated_at = datetime.utcnow()
        models.storage.new(self)
        models.storage.save()

    def to_dict(self):
        """Return a dictionary with all the instance attributes.

        Adds the __class__ key, converts the dates to ISO strings and
        leaves out the SQLAlchemy state and the loaded relationships.
        """
        data = {key: value for key, value in self.__dict__.items()
                if key != "_sa_instance_state" and not _is_related(value)}
        data["__class__"] = type(self).__name__
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data

    def delete(self):
        """Delete the current instance from the storage."""
        models.storage.delete(self)

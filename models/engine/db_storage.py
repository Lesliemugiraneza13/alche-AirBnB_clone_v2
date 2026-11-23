#!/usr/bin/python3
"""Defines the DBStorage class, a MySQL storage engine using SQLAlchemy."""
from os import getenv
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import scoped_session, sessionmaker
from models.base_model import Base
from models.user import User
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.place import Place
from models.review import Review

CLASSES = {"User": User, "State": State, "City": City,
           "Amenity": Amenity, "Place": Place, "Review": Review}


class DBStorage:
    """Stores and retrieves the objects in a MySQL database."""

    __engine = None
    __session = None

    def __init__(self):
        """Create the engine from the environment variables."""
        url = URL.create("mysql+mysqldb",
                         username=getenv("HBNB_MYSQL_USER"),
                         password=getenv("HBNB_MYSQL_PWD"),
                         host=getenv("HBNB_MYSQL_HOST", "localhost"),
                         database=getenv("HBNB_MYSQL_DB"))
        self.__engine = create_engine(url, pool_pre_ping=True)
        if getenv("HBNB_ENV") == "test":
            Base.metadata.drop_all(self.__engine)

    def all(self, cls=None):
        """Return a dictionary of all the objects, optionally of one class.

        cls can be a class or a class name. Keys are <class name>.<id>.
        """
        if isinstance(cls, str):
            cls = CLASSES.get(cls)
            if cls is None:
                return {}
        classes = [cls] if cls is not None else list(CLASSES.values())
        objects = {}
        for kind in classes:
            for obj in self.__session.query(kind).all():
                objects["{}.{}".format(type(obj).__name__, obj.id)] = obj
        return objects

    def new(self, obj):
        """Add obj to the current database session."""
        self.__session.add(obj)

    def save(self):
        """Commit all the changes of the current database session."""
        self.__session.commit()

    def delete(self, obj=None):
        """Delete obj from the current database session if not None."""
        if obj is not None:
            self.__session.delete(obj)

    def reload(self):
        """Create all the tables and the current database session."""
        Base.metadata.create_all(self.__engine)
        factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        self.__session = scoped_session(factory)

    def close(self):
        """Close the current database session."""
        self.__session.remove()

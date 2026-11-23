#!/usr/bin/python3
"""Unit tests for the User class."""
import unittest
from datetime import datetime
from os import getenv
from sqlalchemy import Float, Integer, String
from models import storage
from models.base_model import Base, BaseModel
from models.user import User

DB = getenv("HBNB_TYPE_STORAGE") == "db"


class TestUser(unittest.TestCase):
    """Test the User class."""

    def tearDown(self):
        """Remove the objects created by the tests."""
        if not DB:
            storage.all().clear()

    def test_docstrings(self):
        """Test that the module and the class are documented."""
        import models.user as module
        self.assertTrue(len(module.__doc__) > 5)
        self.assertTrue(len(User.__doc__) > 5)

    def test_inherits_from_base_model_and_base(self):
        """Test the inheritance and its order."""
        self.assertEqual(User.__mro__[1:3], (BaseModel, Base))

    def test_base_attributes(self):
        """Test the attributes inherited from BaseModel."""
        obj = User()
        self.assertIsInstance(obj.id, str)
        self.assertIsInstance(obj.created_at, datetime)
        self.assertIsInstance(obj.updated_at, datetime)

    def test_tablename(self):
        """Test the name of the table."""
        self.assertEqual(User.__tablename__, "users")

    def test_columns(self):
        """Test the type, size and nullability of the columns."""
        columns = User.__table__.columns
        column = columns["email"]
        self.assertIsInstance(column.type, String)
        self.assertEqual(column.type.length, 128)
        self.assertEqual(column.nullable, False)
        column = columns["password"]
        self.assertIsInstance(column.type, String)
        self.assertEqual(column.type.length, 128)
        self.assertEqual(column.nullable, False)
        column = columns["first_name"]
        self.assertIsInstance(column.type, String)
        self.assertEqual(column.type.length, 128)
        self.assertEqual(column.nullable, True)
        column = columns["last_name"]
        self.assertIsInstance(column.type, String)
        self.assertEqual(column.type.length, 128)
        self.assertEqual(column.nullable, True)

    def test_to_dict_and_back(self):
        """Test the round trip through to_dict."""
        obj = User()
        data = obj.to_dict()
        self.assertEqual(data["__class__"], "User")
        self.assertEqual(User(**data).to_dict(), data)

    def test_kwargs_set_attributes(self):
        """Test that attributes can be given to the constructor."""
        obj = User(name="Some name")
        self.assertEqual(obj.name, "Some name")

    @unittest.skipUnless(DB, "DBStorage only")
    def test_relationships(self):
        """Test the places and reviews relationships and their cascade."""
        for name, kind in (("places", "Place"), ("reviews", "Review")):
            relation = getattr(User, name).property
            self.assertEqual(relation.mapper.class_.__name__, kind)
            self.assertEqual(relation.backref, "user")
            self.assertTrue(relation.cascade.delete)


if __name__ == "__main__":
    unittest.main()

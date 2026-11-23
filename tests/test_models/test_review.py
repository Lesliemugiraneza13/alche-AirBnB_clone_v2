#!/usr/bin/python3
"""Unit tests for the Review class."""
import unittest
from datetime import datetime
from os import getenv
from sqlalchemy import Float, Integer, String
from models import storage
from models.base_model import Base, BaseModel
from models.review import Review

DB = getenv("HBNB_TYPE_STORAGE") == "db"


class TestReview(unittest.TestCase):
    """Test the Review class."""

    def tearDown(self):
        """Remove the objects created by the tests."""
        if not DB:
            storage.all().clear()

    def test_docstrings(self):
        """Test that the module and the class are documented."""
        import models.review as module
        self.assertTrue(len(module.__doc__) > 5)
        self.assertTrue(len(Review.__doc__) > 5)

    def test_inherits_from_base_model_and_base(self):
        """Test the inheritance and its order."""
        self.assertEqual(Review.__mro__[1:3], (BaseModel, Base))

    def test_base_attributes(self):
        """Test the attributes inherited from BaseModel."""
        obj = Review()
        self.assertIsInstance(obj.id, str)
        self.assertIsInstance(obj.created_at, datetime)
        self.assertIsInstance(obj.updated_at, datetime)

    def test_tablename(self):
        """Test the name of the table."""
        self.assertEqual(Review.__tablename__, "reviews")

    def test_columns(self):
        """Test the type, size and nullability of the columns."""
        columns = Review.__table__.columns
        column = columns["text"]
        self.assertIsInstance(column.type, String)
        self.assertEqual(column.type.length, 1024)
        self.assertEqual(column.nullable, False)
        column = columns["place_id"]
        self.assertIsInstance(column.type, String)
        self.assertEqual(column.type.length, 60)
        self.assertEqual(column.nullable, False)
        self.assertEqual({k.target_fullname for k in column.foreign_keys},
                         {"places.id"})
        column = columns["user_id"]
        self.assertIsInstance(column.type, String)
        self.assertEqual(column.type.length, 60)
        self.assertEqual(column.nullable, False)
        self.assertEqual({k.target_fullname for k in column.foreign_keys},
                         {"users.id"})

    def test_to_dict_and_back(self):
        """Test the round trip through to_dict."""
        obj = Review()
        data = obj.to_dict()
        self.assertEqual(data["__class__"], "Review")
        self.assertEqual(Review(**data).to_dict(), data)

    def test_kwargs_set_attributes(self):
        """Test that attributes can be given to the constructor."""
        obj = Review(name="Some name")
        self.assertEqual(obj.name, "Some name")


if __name__ == "__main__":
    unittest.main()

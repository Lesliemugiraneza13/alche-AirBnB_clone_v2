#!/usr/bin/python3
"""Unit tests for the Amenity class."""
import unittest
from datetime import datetime
from os import getenv
from sqlalchemy import Float, Integer, String
from models import storage
from models.base_model import Base, BaseModel
from models.amenity import Amenity

DB = getenv("HBNB_TYPE_STORAGE") == "db"


class TestAmenity(unittest.TestCase):
    """Test the Amenity class."""

    def tearDown(self):
        """Remove the objects created by the tests."""
        if not DB:
            storage.all().clear()

    def test_docstrings(self):
        """Test that the module and the class are documented."""
        import models.amenity as module
        self.assertTrue(len(module.__doc__) > 5)
        self.assertTrue(len(Amenity.__doc__) > 5)

    def test_inherits_from_base_model_and_base(self):
        """Test the inheritance and its order."""
        self.assertEqual(Amenity.__mro__[1:3], (BaseModel, Base))

    def test_base_attributes(self):
        """Test the attributes inherited from BaseModel."""
        obj = Amenity()
        self.assertIsInstance(obj.id, str)
        self.assertIsInstance(obj.created_at, datetime)
        self.assertIsInstance(obj.updated_at, datetime)

    def test_tablename(self):
        """Test the name of the table."""
        self.assertEqual(Amenity.__tablename__, "amenities")

    def test_columns(self):
        """Test the type, size and nullability of the columns."""
        columns = Amenity.__table__.columns
        column = columns["name"]
        self.assertIsInstance(column.type, String)
        self.assertEqual(column.type.length, 128)
        self.assertEqual(column.nullable, False)

    def test_to_dict_and_back(self):
        """Test the round trip through to_dict."""
        obj = Amenity()
        data = obj.to_dict()
        self.assertEqual(data["__class__"], "Amenity")
        self.assertEqual(Amenity(**data).to_dict(), data)

    def test_kwargs_set_attributes(self):
        """Test that attributes can be given to the constructor."""
        obj = Amenity(name="Some name")
        self.assertEqual(obj.name, "Some name")

    @unittest.skipUnless(DB, "DBStorage only")
    def test_place_amenities_relationship(self):
        """Test the many-to-many relationship with Place."""
        relation = Amenity.place_amenities.property
        self.assertEqual(relation.mapper.class_.__name__, "Place")
        self.assertEqual(relation.secondary.name, "place_amenity")


if __name__ == "__main__":
    unittest.main()

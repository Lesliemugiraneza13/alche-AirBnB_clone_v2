#!/usr/bin/python3
"""Unit tests for the State class."""
import unittest
from datetime import datetime
from os import getenv
from sqlalchemy import Float, Integer, String
from models import storage
from models.base_model import Base, BaseModel
from models.state import State

DB = getenv("HBNB_TYPE_STORAGE") == "db"


class TestState(unittest.TestCase):
    """Test the State class."""

    def tearDown(self):
        """Remove the objects created by the tests."""
        if not DB:
            storage.all().clear()

    def test_docstrings(self):
        """Test that the module and the class are documented."""
        import models.state as module
        self.assertTrue(len(module.__doc__) > 5)
        self.assertTrue(len(State.__doc__) > 5)

    def test_inherits_from_base_model_and_base(self):
        """Test the inheritance and its order."""
        self.assertEqual(State.__mro__[1:3], (BaseModel, Base))

    def test_base_attributes(self):
        """Test the attributes inherited from BaseModel."""
        obj = State()
        self.assertIsInstance(obj.id, str)
        self.assertIsInstance(obj.created_at, datetime)
        self.assertIsInstance(obj.updated_at, datetime)

    def test_tablename(self):
        """Test the name of the table."""
        self.assertEqual(State.__tablename__, "states")

    def test_columns(self):
        """Test the type, size and nullability of the columns."""
        columns = State.__table__.columns
        column = columns["name"]
        self.assertIsInstance(column.type, String)
        self.assertEqual(column.type.length, 128)
        self.assertEqual(column.nullable, False)

    def test_to_dict_and_back(self):
        """Test the round trip through to_dict."""
        obj = State()
        data = obj.to_dict()
        self.assertEqual(data["__class__"], "State")
        self.assertEqual(State(**data).to_dict(), data)

    def test_kwargs_set_attributes(self):
        """Test that attributes can be given to the constructor."""
        obj = State(name="Some name")
        self.assertEqual(obj.name, "Some name")

    @unittest.skipIf(DB, "FileStorage only")
    def test_cities_getter(self):
        """Test that cities returns the City instances of the State."""
        from models.city import City
        state, other = State(name="A"), State(name="B")
        state.save()
        other.save()
        city = City(name="c", state_id=state.id)
        city.save()
        City(name="d", state_id=other.id).save()
        self.assertEqual(state.cities, [city])

    @unittest.skipUnless(DB, "DBStorage only")
    def test_cities_relationship(self):
        """Test the relationship and cascade options of cities."""
        relation = State.cities.property
        self.assertEqual(relation.mapper.class_.__name__, "City")
        self.assertEqual(relation.backref, "state")
        self.assertTrue(relation.cascade.delete)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/python3
"""Unit tests for the Place class."""
import unittest
from datetime import datetime
from os import getenv
from sqlalchemy import Float, Integer, String
from models import storage
from models.base_model import Base, BaseModel
from models.place import Place

DB = getenv("HBNB_TYPE_STORAGE") == "db"


class TestPlace(unittest.TestCase):
    """Test the Place class."""

    def tearDown(self):
        """Remove the objects created by the tests."""
        if not DB:
            storage.all().clear()

    def test_docstrings(self):
        """Test that the module and the class are documented."""
        import models.place as module
        self.assertTrue(len(module.__doc__) > 5)
        self.assertTrue(len(Place.__doc__) > 5)

    def test_inherits_from_base_model_and_base(self):
        """Test the inheritance and its order."""
        self.assertEqual(Place.__mro__[1:3], (BaseModel, Base))

    def test_base_attributes(self):
        """Test the attributes inherited from BaseModel."""
        obj = Place()
        self.assertIsInstance(obj.id, str)
        self.assertIsInstance(obj.created_at, datetime)
        self.assertIsInstance(obj.updated_at, datetime)

    def test_tablename(self):
        """Test the name of the table."""
        self.assertEqual(Place.__tablename__, "places")

    def test_columns(self):
        """Test the type, size and nullability of the columns."""
        columns = Place.__table__.columns
        column = columns["city_id"]
        self.assertIsInstance(column.type, String)
        self.assertEqual(column.type.length, 60)
        self.assertEqual(column.nullable, False)
        self.assertEqual({k.target_fullname for k in column.foreign_keys},
                         {"cities.id"})
        column = columns["user_id"]
        self.assertIsInstance(column.type, String)
        self.assertEqual(column.type.length, 60)
        self.assertEqual(column.nullable, False)
        self.assertEqual({k.target_fullname for k in column.foreign_keys},
                         {"users.id"})
        column = columns["name"]
        self.assertIsInstance(column.type, String)
        self.assertEqual(column.type.length, 128)
        self.assertEqual(column.nullable, False)
        column = columns["description"]
        self.assertIsInstance(column.type, String)
        self.assertEqual(column.type.length, 1024)
        self.assertEqual(column.nullable, True)
        column = columns["number_rooms"]
        self.assertIsInstance(column.type, Integer)
        self.assertEqual(column.nullable, False)
        column = columns["number_bathrooms"]
        self.assertIsInstance(column.type, Integer)
        self.assertEqual(column.nullable, False)
        column = columns["max_guest"]
        self.assertIsInstance(column.type, Integer)
        self.assertEqual(column.nullable, False)
        column = columns["price_by_night"]
        self.assertIsInstance(column.type, Integer)
        self.assertEqual(column.nullable, False)
        column = columns["latitude"]
        self.assertIsInstance(column.type, Float)
        self.assertEqual(column.nullable, True)
        column = columns["longitude"]
        self.assertIsInstance(column.type, Float)
        self.assertEqual(column.nullable, True)

    def test_to_dict_and_back(self):
        """Test the round trip through to_dict."""
        obj = Place()
        data = obj.to_dict()
        self.assertEqual(data["__class__"], "Place")
        self.assertEqual(Place(**data).to_dict(), data)

    def test_kwargs_set_attributes(self):
        """Test that attributes can be given to the constructor."""
        obj = Place(name="Some name")
        self.assertEqual(obj.name, "Some name")

    @unittest.skipIf(DB, "FileStorage only")
    def test_default_values(self):
        """Test the default values of the number columns."""
        obj = Place()
        self.assertEqual(obj.number_rooms, 0)
        self.assertIsInstance(obj.number_rooms, int)
        self.assertEqual(obj.number_bathrooms, 0)
        self.assertIsInstance(obj.number_bathrooms, int)
        self.assertEqual(obj.max_guest, 0)
        self.assertIsInstance(obj.max_guest, int)
        self.assertEqual(obj.price_by_night, 0)
        self.assertIsInstance(obj.price_by_night, int)

    def test_place_amenity_table(self):
        """Test the place_amenity association table."""
        from models.place import place_amenity
        self.assertEqual(place_amenity.name, "place_amenity")
        self.assertEqual(sorted(place_amenity.columns.keys()),
                         ["amenity_id", "place_id"])
        for column in place_amenity.columns:
            self.assertTrue(column.primary_key)
            self.assertFalse(column.nullable)
            self.assertEqual(column.type.length, 60)

    @unittest.skipIf(DB, "FileStorage only")
    def test_reviews_getter(self):
        """Test that reviews returns the Review instances of the Place."""
        from models.review import Review
        place = Place(name="p", city_id="1", user_id="1")
        place.save()
        review = Review(text="t", place_id=place.id, user_id="1")
        review.save()
        Review(text="t", place_id="other", user_id="1").save()
        self.assertEqual(place.reviews, [review])

    @unittest.skipIf(DB, "FileStorage only")
    def test_amenities_getter_and_setter(self):
        """Test that the setter stores ids and the getter returns objects."""
        from models.amenity import Amenity
        place = Place(name="p", city_id="1", user_id="1")
        amenity = Amenity(name="Wifi")
        amenity.save()
        place.amenities = amenity
        place.amenities = amenity
        place.amenities = "not an amenity"
        self.assertEqual(place.amenity_ids, [amenity.id])
        self.assertEqual(place.amenities, [amenity])
        self.assertEqual(Place.amenity_ids, [])

    @unittest.skipUnless(DB, "DBStorage only")
    def test_relationships(self):
        """Test the reviews and amenities relationships."""
        self.assertEqual(Place.reviews.property.backref, "place")
        self.assertTrue(Place.reviews.property.cascade.delete)
        self.assertEqual(Place.amenities.property.secondary.name,
                         "place_amenity")


if __name__ == "__main__":
    unittest.main()

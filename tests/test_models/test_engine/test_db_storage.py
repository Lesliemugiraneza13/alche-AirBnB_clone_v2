#!/usr/bin/python3
"""Unit tests for the DBStorage class, run with HBNB_TYPE_STORAGE=db."""
import os
import unittest
from os import getenv

DB = getenv("HBNB_TYPE_STORAGE") == "db"


def count_rows(table):
    """Return the number of rows of table, using MySQLdb directly."""
    import MySQLdb
    conn = MySQLdb.connect(host=getenv("HBNB_MYSQL_HOST", "localhost"),
                           user=getenv("HBNB_MYSQL_USER"),
                           passwd=getenv("HBNB_MYSQL_PWD"),
                           db=getenv("HBNB_MYSQL_DB"))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM {}".format(table))
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total


@unittest.skipUnless(DB, "DBStorage only")
class TestDBStorage(unittest.TestCase):
    """Test the DBStorage class against a real MySQL database."""

    def test_docstrings(self):
        """Test that the module, class and methods are documented."""
        import models.engine.db_storage as module
        self.assertTrue(len(module.__doc__) > 5)
        self.assertTrue(len(module.DBStorage.__doc__) > 5)
        for name in ("__init__", "all", "new", "save", "delete", "reload"):
            self.assertTrue(len(getattr(module.DBStorage, name).__doc__) > 5)

    def test_storage_is_db_storage(self):
        """Test that storage is an instance of DBStorage."""
        from models import storage
        from models.engine.db_storage import DBStorage
        self.assertIsInstance(storage, DBStorage)

    def test_new_and_save_add_a_row(self):
        """Test that saving a State adds one row to the states table."""
        from models.state import State
        before = count_rows("states")
        State(name="California").save()
        self.assertEqual(count_rows("states"), before + 1)

    def test_all_returns_dict_by_class(self):
        """Test that all returns <class>.<id> keys, filtered by class."""
        from models import storage
        from models.state import State
        state = State(name="Nevada")
        state.save()
        states = storage.all(State)
        self.assertIsInstance(states, dict)
        self.assertIn("State.{}".format(state.id), states)
        self.assertTrue(all(k.startswith("State.") for k in states))
        self.assertIn("State.{}".format(state.id), storage.all())

    def test_delete_removes_the_row(self):
        """Test that delete followed by save removes the row."""
        from models import storage
        from models.state import State
        state = State(name="Utah")
        state.save()
        before = count_rows("states")
        state.delete()
        storage.save()
        self.assertEqual(count_rows("states"), before - 1)

    def test_deleting_a_state_deletes_its_cities(self):
        """Test the cascade from State to City."""
        from models import storage
        from models.city import City
        from models.state import State
        state = State(name="Texas")
        state.save()
        City(name="Austin", state_id=state.id).save()
        before = count_rows("cities")
        state.delete()
        storage.save()
        self.assertEqual(count_rows("cities"), before - 1)

    def test_console_create_adds_a_row(self):
        """Test that the create command adds a record to the table."""
        from console import HBNBCommand
        before = count_rows("states")
        HBNBCommand().onecmd('create State name="California"')
        self.assertEqual(count_rows("states"), before + 1)

    def test_many_to_many_places_amenities(self):
        """Test that linking an Amenity to a Place fills place_amenity."""
        from models import storage
        from models.amenity import Amenity
        from models.city import City
        from models.place import Place
        from models.state import State
        from models.user import User
        state = State(name="Oregon")
        state.save()
        city = City(name="Portland", state_id=state.id)
        city.save()
        user = User(email="a@b.c", password="pwd")
        user.save()
        place = Place(name="House", city_id=city.id, user_id=user.id)
        place.save()
        amenity = Amenity(name="Wifi")
        amenity.save()
        before = count_rows("place_amenity")
        place.amenities.append(amenity)
        storage.save()
        self.assertEqual(count_rows("place_amenity"), before + 1)


if __name__ == "__main__":
    unittest.main()

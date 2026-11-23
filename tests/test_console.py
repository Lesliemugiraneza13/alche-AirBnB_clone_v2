#!/usr/bin/python3
"""Unit tests for the console create command with parameters."""
import io
import os
import unittest
from contextlib import redirect_stdout
from os import getenv
from console import HBNBCommand, parse_value
from models import storage

DB = getenv("HBNB_TYPE_STORAGE") == "db"


class TestParseValue(unittest.TestCase):
    """Test the conversion of parameter values."""

    def test_string(self):
        """Test that strings lose their quotes and underscores."""
        self.assertEqual(parse_value('"My_little_house"'), "My little house")

    def test_escaped_quote(self):
        """Test that escaped double quotes are kept in the string."""
        self.assertEqual(parse_value('"say_\\"hi\\""'), 'say "hi"')

    def test_integer(self):
        """Test the integer values."""
        self.assertEqual(parse_value("42"), 42)
        self.assertIsInstance(parse_value("-3"), int)

    def test_float(self):
        """Test the float values."""
        self.assertEqual(parse_value("37.773972"), 37.773972)
        self.assertIsInstance(parse_value("-122.43"), float)

    def test_quoted_number_stays_a_string(self):
        """Test that a number between quotes is a string."""
        self.assertEqual(parse_value('"0001"'), "0001")

    def test_invalid_values(self):
        """Test that unrecognized values raise ValueError."""
        for raw in ('"open', "abc", "1.2.3", '"'):
            with self.assertRaises(ValueError):
                parse_value(raw)


@unittest.skipIf(DB, "FileStorage only")
class TestCreate(unittest.TestCase):
    """Test the create command with the FileStorage engine."""

    def setUp(self):
        """Move any existing file.json out of the way and empty storage."""
        if os.path.exists("file.json"):
            os.rename("file.json", "tmp_file.json")
        self.saved = dict(storage.all())
        storage.all().clear()

    def tearDown(self):
        """Restore storage and the original file.json."""
        storage.all().clear()
        storage.all().update(self.saved)
        if os.path.exists("file.json"):
            os.remove("file.json")
        if os.path.exists("tmp_file.json"):
            os.rename("tmp_file.json", "file.json")

    def run_command(self, line):
        """Run one console command and return what it printed."""
        out = io.StringIO()
        with redirect_stdout(out):
            HBNBCommand().onecmd(line)
        return out.getvalue().strip()

    def test_create_prints_id_and_stores(self):
        """Test that create prints the id of a stored instance."""
        new_id = self.run_command("create State name=\"California\"")
        self.assertIn("State." + new_id, storage.all())

    def test_create_with_params(self):
        """Test the str, int and float parameters of the Place example."""
        new_id = self.run_command(
            'create Place city_id="0001" user_id="0001" '
            'name="My_little_house" number_rooms=4 number_bathrooms=2 '
            'max_guest=10 price_by_night=300 latitude=37.773972 '
            'longitude=-122.431297')
        place = storage.all()["Place." + new_id]
        self.assertEqual(place.name, "My little house")
        self.assertEqual(place.number_rooms, 4)
        self.assertEqual(place.latitude, 37.773972)
        self.assertEqual(place.longitude, -122.431297)
        self.assertEqual(place.city_id, "0001")

    def test_invalid_params_are_skipped(self):
        """Test that unrecognized parameters are ignored."""
        new_id = self.run_command(
            'create State name="Texas" bad=value open="oops count=5')
        state = storage.all()["State." + new_id]
        self.assertEqual(state.name, "Texas")
        self.assertFalse(hasattr(state, "bad"))
        self.assertEqual(state.count, 5)

    def test_create_is_saved_in_the_file(self):
        """Test that the new instance is written to file.json."""
        self.run_command('create State name="Arizona"')
        with open("file.json", encoding="utf-8") as f:
            self.assertIn("Arizona", f.read())

    def test_errors(self):
        """Test the error messages of create."""
        self.assertEqual(self.run_command("create"),
                         "** class name missing **")
        self.assertEqual(self.run_command("create MyModel"),
                         "** class doesn't exist **")

    def test_destroy_and_show(self):
        """Test that destroy deletes an instance created with create."""
        new_id = self.run_command('create State name="Utah"')
        self.assertIn("Utah", self.run_command("show State " + new_id))
        self.run_command("destroy State " + new_id)
        self.assertEqual(self.run_command("show State " + new_id),
                         "** no instance found **")

    def test_all_by_class(self):
        """Test that all filters by class name."""
        self.run_command('create State name="Utah"')
        self.run_command('create City name="X" state_id="1"')
        self.assertIn("State", self.run_command("all State"))
        self.assertNotIn("City", self.run_command("all State"))
        self.assertEqual(self.run_command("all MyModel"),
                         "** class doesn't exist **")

    def test_update_casts_to_column_type(self):
        """Test that update casts the value to the column type."""
        new_id = self.run_command(
            'create Place city_id="1" user_id="1" name="P"')
        self.run_command("update Place {} number_rooms 3".format(new_id))
        self.run_command("update Place {} name 123".format(new_id))
        place = storage.all()["Place." + new_id]
        self.assertEqual(place.number_rooms, 3)
        self.assertEqual(place.name, "123")


if __name__ == "__main__":
    unittest.main()

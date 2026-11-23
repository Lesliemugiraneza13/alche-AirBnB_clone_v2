#!/usr/bin/python3
"""Unit tests for the BaseModel class."""
import os
import unittest
from datetime import datetime
from os import getenv
from models import storage
from models.base_model import BaseModel

DB = getenv("HBNB_TYPE_STORAGE") == "db"


class TestBaseModel(unittest.TestCase):
    """Test the BaseModel class."""

    def setUp(self):
        """Move any existing file.json out of the way."""
        if os.path.exists("file.json"):
            os.rename("file.json", "tmp_file.json")

    def tearDown(self):
        """Remove the test file.json and restore the original one."""
        if os.path.exists("file.json"):
            os.remove("file.json")
        if os.path.exists("tmp_file.json"):
            os.rename("tmp_file.json", "file.json")

    def test_docstrings(self):
        """Test that the module, class and methods are documented."""
        import models.base_model as module
        self.assertTrue(len(module.__doc__) > 5)
        self.assertTrue(len(BaseModel.__doc__) > 5)
        for name in ("__init__", "__str__", "save", "to_dict", "delete"):
            self.assertTrue(len(getattr(BaseModel, name).__doc__) > 5)

    def test_id_is_unique_string(self):
        """Test that each instance gets a different string id."""
        a, b = BaseModel(), BaseModel()
        self.assertIsInstance(a.id, str)
        self.assertNotEqual(a.id, b.id)

    def test_dates_are_datetimes(self):
        """Test the type and initial value of the date attributes."""
        model = BaseModel()
        self.assertIsInstance(model.created_at, datetime)
        self.assertIsInstance(model.updated_at, datetime)
        self.assertEqual(model.created_at, model.updated_at)

    def test_column_definitions(self):
        """Test the SQLAlchemy columns declared on BaseModel."""
        from sqlalchemy import DateTime, String
        self.assertIsInstance(BaseModel.id.type, String)
        self.assertEqual(BaseModel.id.type.length, 60)
        self.assertTrue(BaseModel.id.primary_key)
        self.assertFalse(BaseModel.id.nullable)
        for column in (BaseModel.created_at, BaseModel.updated_at):
            self.assertIsInstance(column.type, DateTime)
            self.assertFalse(column.nullable)
            self.assertIsNotNone(column.default)

    def test_does_not_inherit_from_base(self):
        """Test that BaseModel itself is not a mapped class."""
        from models.base_model import Base
        self.assertFalse(issubclass(BaseModel, Base))

    def test_str(self):
        """Test the string representation."""
        model = BaseModel()
        expected = "[BaseModel] ({}) {}".format(model.id, model.__dict__)
        self.assertEqual(str(model), expected)

    def test_str_hides_sqlalchemy_state(self):
        """Test that _sa_instance_state is not printed."""
        model = BaseModel()
        model._sa_instance_state = "hidden"
        self.assertNotIn("_sa_instance_state", str(model))

    def test_to_dict(self):
        """Test the content of the dictionary representation."""
        model = BaseModel()
        model.name = "My Model"
        data = model.to_dict()
        self.assertEqual(data["__class__"], "BaseModel")
        self.assertEqual(data["name"], "My Model")
        self.assertEqual(data["id"], model.id)
        self.assertEqual(data["created_at"], model.created_at.isoformat())
        self.assertEqual(data["updated_at"], model.updated_at.isoformat())

    def test_to_dict_removes_sqlalchemy_state(self):
        """Test that _sa_instance_state is removed only if it exists."""
        model = BaseModel()
        self.assertNotIn("_sa_instance_state", model.to_dict())
        model._sa_instance_state = "hidden"
        self.assertNotIn("_sa_instance_state", model.to_dict())
        self.assertIn("_sa_instance_state", model.__dict__)

    def test_to_dict_does_not_change_instance(self):
        """Test that to_dict leaves the instance attributes untouched."""
        model = BaseModel()
        model.to_dict()
        self.assertNotIn("__class__", model.__dict__)
        self.assertIsInstance(model.created_at, datetime)

    def test_from_dict(self):
        """Test re-creating an instance from its dictionary."""
        model = BaseModel()
        model.name = "My Model"
        new = BaseModel(**model.to_dict())
        self.assertIsNot(model, new)
        self.assertEqual(new.id, model.id)
        self.assertEqual(new.name, "My Model")
        self.assertEqual(new.created_at, model.created_at)
        self.assertNotIn("__class__", new.__dict__)
        self.assertEqual(new.to_dict(), model.to_dict())

    def test_kwargs_set_attributes(self):
        """Test that kwargs become instance attributes."""
        model = BaseModel(name="California", number=3)
        self.assertEqual(model.name, "California")
        self.assertEqual(model.number, 3)
        self.assertIsInstance(model.id, str)

    def test_args_are_ignored(self):
        """Test that positional arguments are not used."""
        model = BaseModel("ignored", 89)
        self.assertNotIn("ignored", model.__dict__.values())

    @unittest.skipIf(DB, "FileStorage only")
    def test_not_stored_before_save(self):
        """Test that a new instance is only stored once it is saved."""
        model = BaseModel()
        self.assertNotIn("BaseModel.{}".format(model.id), storage.all())

    @unittest.skipIf(DB, "FileStorage only")
    def test_save_stores_and_writes_file(self):
        """Test that save registers the instance and writes the file."""
        model = BaseModel()
        model.save()
        self.assertIn("BaseModel.{}".format(model.id), storage.all())
        self.assertTrue(os.path.exists("file.json"))

    @unittest.skipIf(DB, "FileStorage only")
    def test_save_updates_updated_at(self):
        """Test that save changes updated_at only."""
        model = BaseModel()
        first, created = model.updated_at, model.created_at
        model.save()
        self.assertGreater(model.updated_at, first)
        self.assertEqual(model.created_at, created)

    @unittest.skipIf(DB, "FileStorage only")
    def test_delete_removes_from_storage(self):
        """Test that delete removes the instance from the storage."""
        model = BaseModel()
        model.save()
        model.delete()
        self.assertNotIn("BaseModel.{}".format(model.id), storage.all())

    @unittest.skipIf(DB, "FileStorage only")
    def test_instance_from_dict_is_not_stored(self):
        """Test that rebuilding from a dict does not store the instance."""
        data = BaseModel().to_dict()
        count = len(storage.all())
        BaseModel(**data)
        self.assertEqual(len(storage.all()), count)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/python3
"""Defines the FileStorage class, a JSON file storage engine."""
import json
from models.base_model import BaseModel
from models.user import User
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.place import Place
from models.review import Review

CLASSES = {"BaseModel": BaseModel, "User": User, "State": State,
           "City": City, "Amenity": Amenity, "Place": Place,
           "Review": Review}


class FileStorage:
    """Serializes instances to a JSON file and deserializes them back."""

    __file_path = "file.json"
    __objects = {}

    def all(self, cls=None):
        """Return the dictionary of stored objects, optionally of one class.

        cls can be a class or a class name.
        """
        if cls is None:
            return FileStorage.__objects
        name = cls if isinstance(cls, str) else cls.__name__
        return {key: obj for key, obj in FileStorage.__objects.items()
                if type(obj).__name__ == name}

    def new(self, obj):
        """Store obj in __objects with the key <class name>.id."""
        key = "{}.{}".format(type(obj).__name__, obj.id)
        FileStorage.__objects[key] = obj

    def save(self):
        """Serialize __objects to the JSON file __file_path."""
        data = {key: obj.to_dict()
                for key, obj in FileStorage.__objects.items()}
        with open(FileStorage.__file_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def reload(self):
        """Deserialize the JSON file to __objects, if the file exists."""
        try:
            with open(FileStorage.__file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            return
        for key, value in data.items():
            FileStorage.__objects[key] = CLASSES[value["__class__"]](**value)

    def delete(self, obj=None):
        """Delete obj from __objects if it is inside, do nothing if None."""
        if obj is None:
            return
        key = "{}.{}".format(type(obj).__name__, obj.id)
        FileStorage.__objects.pop(key, None)

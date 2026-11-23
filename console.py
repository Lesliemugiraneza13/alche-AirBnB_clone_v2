#!/usr/bin/python3
"""Entry point of the AirBnB clone command interpreter."""
import cmd
import re
import shlex
from models import storage
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

PARAM = re.compile(r'(\w+)=("(?:[^"\\]|\\.)*"|\S+)')


def parse_value(raw):
    """Convert the raw text of a parameter value to a str, int or float.

    Raise ValueError if the text does not fit the value syntax.
    """
    if raw.startswith('"'):
        if len(raw) < 2 or not raw.endswith('"'):
            raise ValueError(raw)
        return raw[1:-1].replace('\\"', '"').replace("_", " ")
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    if re.fullmatch(r"-?\d+\.\d+", raw):
        return float(raw)
    raise ValueError(raw)


def cast(value, obj, name):
    """Cast the string value to the type of the attribute name of obj."""
    kind = None
    table = getattr(obj, "__table__", None)
    if table is not None and name in table.columns:
        try:
            kind = table.columns[name].type.python_type
        except NotImplementedError:
            kind = None
    current = getattr(obj, name, None)
    if kind is None and isinstance(current, (int, float, str)):
        kind = type(current)
    if kind in (int, float, str):
        try:
            return kind(value)
        except ValueError:
            return value
    for guess in (int, float):
        try:
            return guess(value)
        except ValueError:
            continue
    return value


class HBNBCommand(cmd.Cmd):
    """Command interpreter used to manage the AirBnB objects."""

    prompt = "(hbnb) "

    def emptyline(self):
        """Do nothing when an empty line is entered."""
        pass

    def do_quit(self, arg):
        """Quit command to exit the program
        """
        return True

    def do_EOF(self, arg):
        """EOF (Ctrl+D) exits the program
        """
        print()
        return True

    def _parse(self, arg, need_id=True):
        """Validate the arguments and return (args, instance) or None.

        Prints the matching error message when an argument is invalid.
        """
        try:
            args = shlex.split(arg)
        except ValueError:
            args = arg.split()
        if not args:
            print("** class name missing **")
            return None
        if args[0] not in CLASSES:
            print("** class doesn't exist **")
            return None
        if not need_id:
            return args, None
        if len(args) < 2:
            print("** instance id missing **")
            return None
        key = "{}.{}".format(args[0], args[1])
        obj = storage.all(CLASSES[args[0]]).get(key)
        if obj is None:
            print("** no instance found **")
            return None
        return args, obj

    def do_create(self, arg):
        """Create a new instance with optional parameters, print its id
        Usage: create <class name> <key>=<value> <key>=<value> ...
        Strings use double quotes and _ for spaces, e.g. name="My_house"
        """
        args = arg.split(None, 1)
        if not args:
            print("** class name missing **")
            return
        if args[0] not in CLASSES:
            print("** class doesn't exist **")
            return
        params = {}
        if len(args) > 1:
            for key, raw in PARAM.findall(args[1]):
                try:
                    params[key] = parse_value(raw)
                except ValueError:
                    continue
        obj = CLASSES[args[0]](**params)
        obj.save()
        print(obj.id)

    def do_show(self, arg):
        """Print the string representation of an instance
        Usage: show <class name> <id>
        """
        parsed = self._parse(arg)
        if parsed:
            print(parsed[1])

    def do_destroy(self, arg):
        """Delete an instance and save the change
        Usage: destroy <class name> <id>
        """
        parsed = self._parse(arg)
        if parsed:
            storage.delete(parsed[1])
            storage.save()

    def do_all(self, arg):
        """Print all instances, optionally only those of one class
        Usage: all [class name]
        """
        if arg.strip():
            parsed = self._parse(arg, need_id=False)
            if not parsed:
                return
            objects = storage.all(CLASSES[parsed[0][0]])
        else:
            objects = storage.all()
        print([str(obj) for obj in objects.values()])

    def do_update(self, arg):
        """Update an attribute of an instance and save the change
        Usage: update <class name> <id> <attribute name> "<attribute value>"
        """
        parsed = self._parse(arg)
        if not parsed:
            return
        args, obj = parsed
        if len(args) < 3:
            print("** attribute name missing **")
            return
        if len(args) < 4:
            print("** value missing **")
            return
        setattr(obj, args[2], cast(args[3], obj, args[2]))
        obj.save()


if __name__ == '__main__':
    HBNBCommand().cmdloop()

# AirBnB Clone - MySQL (v2)

## Description

AirBnB clone is a multi-step project whose goal is to build a simplified copy
of the AirBnB website. This second step keeps the command interpreter and the
`FileStorage` engine from the first step and adds a **MySQL storage engine**
(`DBStorage`) built with the SQLAlchemy ORM. The same code runs with either
engine; an environment variable selects which one is used.

## Storage engines

| Engine | Selected with | Persistence |
| --- | --- | --- |
| `FileStorage` | `HBNB_TYPE_STORAGE` unset or `file` | JSON file `file.json` |
| `DBStorage` | `HBNB_TYPE_STORAGE=db` | MySQL tables |

Both engines expose the same methods: `all(cls=None)`, `new(obj)`,
`save()`, `delete(obj=None)` and `reload()`.

### Environment variables

| Variable | Meaning |
| --- | --- |
| `HBNB_ENV` | `dev` or `test`; with `test`, `DBStorage` drops all tables at start |
| `HBNB_MYSQL_USER` | MySQL user name |
| `HBNB_MYSQL_PWD` | MySQL password |
| `HBNB_MYSQL_HOST` | MySQL host |
| `HBNB_MYSQL_DB` | MySQL database name |
| `HBNB_TYPE_STORAGE` | `file` (FileStorage) or `db` (DBStorage) |

## Requirements

- Ubuntu 20.04 LTS, Python 3.8.5, `pycodestyle` 2.7.*
- MySQL 8.0, SQLAlchemy 1.4.x and `mysqlclient` (the `MySQLdb` driver)

## MySQL setup

Prepare the development and test databases and users (run once, as root):

```
cat setup_mysql_dev.sql | mysql -hlocalhost -uroot -p
cat setup_mysql_test.sql | mysql -hlocalhost -uroot -p
```

| | Development | Test |
| --- | --- | --- |
| Database | `hbnb_dev_db` | `hbnb_test_db` |
| User | `hbnb_dev` | `hbnb_test` |
| Password | `hbnb_dev_pwd` | `hbnb_test_pwd` |

Each user has all privileges on its own database and `SELECT` on
`performance_schema`. The scripts can be run again without failing.

## The command interpreter

Start it in interactive or non-interactive mode, with either engine:

```
./console.py
echo 'all State' | ./console.py

echo 'create State name="California"' | HBNB_MYSQL_USER=hbnb_dev \
HBNB_MYSQL_PWD=hbnb_dev_pwd HBNB_MYSQL_HOST=localhost \
HBNB_MYSQL_DB=hbnb_dev_db HBNB_TYPE_STORAGE=db ./console.py
```

### Commands

| Command | Usage | Description |
| --- | --- | --- |
| `help` | `help [command]` | Lists commands, or shows help for one command |
| `quit` / `EOF` | `quit` | Exits the program |
| `create` | `create <class name> [<key>=<value> ...]` | Creates an instance with optional parameters, saves it and prints its id |
| `show` | `show <class name> <id>` | Prints an instance |
| `destroy` | `destroy <class name> <id>` | Deletes an instance and saves the change |
| `all` | `all [class name]` | Prints all instances, optionally of one class |
| `update` | `update <class name> <id> <attribute name> "<attribute value>"` | Updates one attribute and saves the change |

### Parameters of `create`

Each parameter is `<key name>=<value>`, where the value is:

- a **string**: between double quotes, `_` is replaced by a space and an
  inner double quote is written `\"` (`name="My_little_house"`)
- a **float**: contains a dot (`latitude=37.773972`)
- an **integer**: any other number (`number_rooms=4`)

A parameter that does not fit these rules is skipped.

```
(hbnb) create State name="California"
(hbnb) create Place city_id="0001" user_id="0001" name="My_little_house" number_rooms=4 price_by_night=300 latitude=37.773972
```

### Classes

`BaseModel`, `User`, `State`, `City`, `Amenity`, `Place`, `Review`

| Class | Table | Relationships (DBStorage) |
| --- | --- | --- |
| `State` | `states` | `cities` (deleting a state deletes its cities) |
| `City` | `cities` | `places` |
| `User` | `users` | `places`, `reviews` |
| `Place` | `places` | `reviews`, `amenities` (many-to-many through `place_amenity`) |
| `Review` | `reviews` | |
| `Amenity` | `amenities` | `place_amenities` |

With `FileStorage`, `State.cities`, `Place.reviews` and `Place.amenities` are
properties that look the related objects up in the storage.

## Testing

```
python3 -m unittest discover tests
```

With MySQL (tests for the database engine run only in this mode):

```
HBNB_ENV=test HBNB_MYSQL_USER=hbnb_test HBNB_MYSQL_PWD=hbnb_test_pwd \
HBNB_MYSQL_HOST=localhost HBNB_MYSQL_DB=hbnb_test_db HBNB_TYPE_STORAGE=db \
python3 -m unittest discover tests
```

Tests that only make sense for one engine are skipped for the other with
`unittest.skipIf` / `unittest.skipUnless`.

## Authors

See the [AUTHORS](AUTHORS) file for the list of contributors, which keeps the
authors of the original codebase.

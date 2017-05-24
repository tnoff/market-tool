from copy import deepcopy
import unittest

from jsonschema import validate, ValidationError

from market_tool import schema
from tests import utils

class TestSchema(unittest.TestCase):
    def test_schema(self):
        database_schema = schema.DATABASE_SCHEMA
        valid_sqlite = {
            'sqlite' : {
                'database_file' : utils.random_string(suffix='.sql'),
            },
        }
        validate(valid_sqlite, database_schema)

        valid_mysql = {
            'mysql' : {
                'username' : utils.random_string(),
                'password' : utils.random_string(),
                'host' : utils.random_string(),
                'database_name' : utils.random_string(),
            },
        }
        validate(valid_mysql, database_schema)

        # make sure all args are required
        invalid_sqlite = {
            'sqlite' : {},
        }
        with self.assertRaises(ValidationError):
            validate(invalid_sqlite, database_schema)

        for key in valid_mysql['mysql']:
            invalid_mysql = deepcopy(valid_mysql)
            invalid_mysql['mysql'].pop(key)
            with self.assertRaises(ValidationError):
                validate(invalid_mysql, database_schema)

        for key in valid_mysql['mysql']:
            invalid_mysql = deepcopy(valid_mysql)
            invalid_mysql['mysql'][key] = None
            with self.assertRaises(ValidationError):
                validate(invalid_mysql, database_schema)

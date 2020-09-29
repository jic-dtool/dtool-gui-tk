"""Module for working with metadata schemas.

Example usage:

>>> from metadata import MetadataSchemaItem
>>> nucl_acid = MetadataSchemaItem({"type": "string", "enum": ["DNA", "RNA"]})
>>> nucl_acid.type
'string'
>>> nucl_acid.enum
['DNA', 'RNA']
>>> print(nucl_acid.is_okay("RNA"))
True
>>> print(nucl_acid.is_okay("Not DNA"))
False
>>> for i in nucl_acid.issues("Not DNA"):
...     print(i)
...
'Not DNA' is not one of ['DNA', 'RNA']
"""

import jsonschema
import jsonschema.exceptions
import jsonschema.validators


class SchemaError(jsonschema.exceptions.SchemaError):
    pass


class MetadataSchemaItem(object):

    def __init__(self, schema):
        self._schema = schema
        self._ivalidator = jsonschema.validators.Draft7Validator(schema)

        # Ensure that the schema is valid.
        try:
            jsonschema.validate(None, self._schema)
        except jsonschema.exceptions.ValidationError:
            pass
        except jsonschema.exceptions.SchemaError as e:
            raise(SchemaError(e))

    @property
    def type(self):
        return self._schema["type"]

    @property
    def enum(self):
        return self._schema.get("enum", None)

    def is_okay(self, value):
        try:
            jsonschema.validate(value, self._schema)
        except jsonschema.exceptions.ValidationError:
            return False
        return True

    def issues(self, value):
        return [i.message for i in self._ivalidator.iter_errors(value)]
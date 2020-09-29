"""Test the metadata module."""

import pytest


def test_basic_string_metadata():
    from metadata import MetadataSchemaItem

    string_schema = MetadataSchemaItem({"type": "string"})
    assert string_schema.type == "string"
    assert string_schema.enum is None

    assert string_schema.is_okay("test")

    assert not string_schema.is_okay(1)


def test_enum_integer_metadata():

    from metadata import MetadataSchemaItem

    enum_int_schema = MetadataSchemaItem(
        {"type": "integer", "enum": [1, 2, 3]}
    )

    assert enum_int_schema.type == "integer"
    assert enum_int_schema.enum == [1, 2, 3]

    assert enum_int_schema.is_okay(1)

    assert not enum_int_schema.is_okay(4)

    assert not enum_int_schema.is_okay(1.1)


def test_invalid_schema():

    from metadata import MetadataSchemaItem
    from metadata import SchemaError

    with pytest.raises(SchemaError):
        MetadataSchemaItem({"type": "dontexist"})


def test_issues_method():
    from metadata import MetadataSchemaItem

    complex_array_schema = MetadataSchemaItem({
        "type": "array",
        "items": {"enum": [1, 2, 3]},
        "maxItems": 2
    })

    assert complex_array_schema.is_okay([1, 2])
    assert len(complex_array_schema.issues([1, 2])) == 0

    assert not complex_array_schema.is_okay([1, 2, 4])
    issues = complex_array_schema.issues([1, 2, 4])
    assert len(issues) == 2
    expected_issues = [
        '4 is not one of [1, 2, 3]',
        '[1, 2, 4] is too long'
    ]
    assert sorted(issues, key=str) == expected_issues

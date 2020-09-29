"""Test the metadata module."""

import pytest


def test_basic_string_metadata():
    from metadata import MetadataSchemaItem
    from metadata import ValidationError

    string_schema = MetadataSchemaItem({"type": "string"})
    assert string_schema.type == "string"
    assert string_schema.enum is None

    assert string_schema.validate("test") is None

    with pytest.raises(ValidationError):
        string_schema.validate(1)


def test_enum_integer_metadata():

    from metadata import MetadataSchemaItem
    from metadata import ValidationError

    enum_int_schema = MetadataSchemaItem(
        {"type": "integer", "enum": [1, 2, 3]}
    )

    assert enum_int_schema.type == "integer"
    assert enum_int_schema.enum == [1, 2, 3]

    assert enum_int_schema.validate(1) is None

    with pytest.raises(ValidationError):
        enum_int_schema.validate(4)

    with pytest.raises(ValidationError):
        enum_int_schema.validate(1.1)


def test_invalid_schema():

    from metadata import MetadataSchemaItem
    from metadata import SchemaError

    with pytest.raises(SchemaError):
        MetadataSchemaItem({"type": "dontexist"})


def test_issues_method():
    from metadata import MetadataSchemaItem
    from metadata import ValidationError

    complex_array_schema = MetadataSchemaItem({
        "type": "array",
        "items": {"enum": [1, 2, 3]},
        "maxItems": 2
    })

    assert complex_array_schema.validate([1, 2]) is None

    with pytest.raises(ValidationError):
        complex_array_schema.validate([1, 2, 4])

    assert len(complex_array_schema.issues([1, 2])) == 0

    issues = complex_array_schema.issues([1, 2, 4])
    assert len(issues) == 2
    expected_issues = [
        '4 is not one of [1, 2, 3]',
        '[1, 2, 4] is too long'
    ]
    print(issues)
    assert sorted(issues, key=str) == expected_issues

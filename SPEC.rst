Specification for dtool-gui
===========================

dtool-gui is a graphical user interface to dtool functionality.

Features
--------

1. Create new datasets
2. Display information about a dataset
3. Edit the metadata of a dataset
4. Copy a dataset to a different location
5. List datasets 
6. Search for datasets

Dataset creation red route
--------------------------

Becky the biologist has a directory full of photos of plants that she wants to
mark up as a dataset in order to save them to the institutes raw data storage
system.

On her Windows laptop Becky starts the dtool-gui by clicking on an icon on her
desktop. The GUI opens and she clicks the button named "New Dataset".  The
dtool-gui then shows a pane with five areas:

1. Directory for dataset (defaults to the users home directory)
2. Directory with data files (no default)
3. Add tag
4. Metadata template
5. Freeze dataset

When clicking (1) and (2) above a file browser is opened and Becky can navigate
to the directory where she wants the dataset to be saved and the directory
where the data files are located.

The "Add tag" area displays the users five most popular tags and has an input
field where a new tag can be created along with an "Add" button. Becky clicks
the tags "leaves" and "photos", which are two of her favourite tags, and
manually adds the tag "senescence".

The metadata template area (4) displays an empty pair of key/value cells and an
"Add" button. Above this there is a drop down menu where Becky can select an
existing template of key/value pairs. Becky selects a template she created
previously named "photos". The metadata template area is then populated with
keys that can not be edited. The values from the template include both free
text fields and drop-down menus of predefined options for the value field.
Becky selects options from the drop down menus and enters text into the free
text fields. In one instance where the template has a key/value pair that does
not apply to this dataset she selects the ignore check box next to it.

The freeze dataset area (5) only contains a button called "Freeze dataset".
Becky presses the button and a progress bar shows her that the dtool-gui is
busy freezing here dataset.  Once the dataset is frozen a dialogue displaying
the URI of the frozen dataset pops up.


Metadata template creation red route
------------------------------------

Dora the data manager is helping Becky and the other biologists in the lab
manage their data. She has helped them work out what types of datasets they will
be creating and what metadata each type of dataset needs to have. In order to
make it easier for the biologists Dexter works with them to create metadata
templates for them, where, when possible, valid values are predefined.

Dora works with Becky to create the template and clicks on the dtool-gui
desktop icon on Becky's laptop. Dora then clicks the "New metadata template"
button. The dtool-gui then shows a pane with:

1. A text field for the name of metadata template
2. An area with widgets for adding fields to the template
3. A button for saving the template

The area with widgets for adding fields (2) to the template consists of:

1. A text pane for the "Metadata key"
2. Radio buttons where the metadata type can be specified (text, int, float)
3. Radio buttons where the mode of entry can be specified (manual, select)
4. "Add metadata field" button

Dora starts off by typing "species" into the "Metadata key" text pane (1).
She leaves the "text" radio button selected (the default). However, because
the lab only works on two species she changes the mode of entry radio button
from "manual" to "select". A text box appears and next to it a button named
"Add option". She enters the text "A. thaliana" and presses the "Add option"
button. She then enters the text "M. berteroana" and presses the "Add option"
button again. Finally she presses the "Add metadata field" button.

Dora then enters the text "temperature" into the "Metadata key", selects the
"float" radio button to specify the type, leaves the "manual" radio button
selected, and presses the "Add metadata field" to add another medata field to
the template

Once Dora has added all the metadata fields she presses the "Save template"
button.


Technical details
-----------------

There will be a ``Model`` class which will act as the model in
the Model View Controller (MVC) pattern. This will initially need Create Read
Update Delete (CRUD) functionality to manage:

- Base URIs
- Flat metadata schemas
- Dataset metadata

This means that there will be three models.

- ``BaseURIModel``
- ``MetadataModel``
- ``DatasetModel``

In later releases the ``Model`` will also include CRUD functionality to manage:

- Remote base URI credentials
- Nested metadata schemas

There will be several View classes.

- ``DataSetListView`` that lists all the datasets in the currently selected base URI
- ``DataSetView`` that displays information about the currently selected dataset
- ``UpdateMetaDataView`` that displays a form for updating the currently selected dataset's metadata
- ``CreateDataSetView`` that displays a form for creating a dataset

The ``Controller`` class will know about the Model and the Views and will be
responsible for updating the model and the view in response to the user driven
events. For sample code implementing this pattern using tkinter see:
https://gist.github.com/ajfigueroa/c2af555630d1db3efb5178ece728b017


Metadata schema
---------------

Metadata schemas will be defined using ``JSON Schema`` format. See for example,
`Understanding JSON Schema
<http://json-schema.org/understanding-json-schema/index.html>`_.

Support for JSON Schema in Python can be found in the
`jsonschema package<https://python-jsonschema.readthedocs.io>`_.


Example code
------------

The code below illustrates how to work with the ``BaseURIModel`` class.

.. code-block:: python

    >>> from dtool_gui import BaseURIModel
    >>> base_uri_model = BaseURIModel()

The ``model`` instance can be used to manage base URIs.

.. code-block:: python

    >>> base_uri_model.add_base_uri("file:///home/olssont/datasets")
    >>> base_uri_model.add_base_uri("s3://dtool-demo")
    >>> assert model.list_base_uris() == ["file:///home/olssont/datasets", "s3://dtool-demo"]
    >>> base_uri_model.update_base_uri("s3://dtool-demo", "s3://dtool-testing")
    >>> assert model.list_base_uris() == ["file:///home/olssont/datasets", "s3://dtool-testing"]
    >>> base_uri_model.delete_base_uri("s3://dtool-testing")
    >>> assert model.list_base_uris() == ["file:///home/olssont/datasets"]

The ``MetadataModel`` is used to manage and work with schema items.
The code below adds three metadata schema items.

.. code-block:: python

    >>> from dtool_gui import MetadataModel
    >>> metadata_model = MetadataModel()
    >>> metadata_model.add_schema_item(key_name="project", schema={"type": "string"})
    >>> metadata_model.add_schema_item(key_name="age", schema={"type": "integer"})
    >>> metadata_model.add_schema_item(key_name="nucleic_acid_type", schema={"type": "string", "enum": ["DNA", "RNA"]})

It is possible to list the metadata schema items by name.

.. code-block:: python

    >>> metadata_model.metadata_schema.keys()
    ["age", "nucleic_acid_type", "project"]

It is possible to work with a ``MetaDataSchemaItem`` instance.

.. code-block:: python

    >>> project_schema = metadata_model.metadata_schema["project"]
    >>> print(project_schema.type)
    'string'
    >>> print(project_schema.options)
    None
    >>> print(metadata_model.metadata_schema["nucleic_acid_type"].options)
    ["DNA", "RNA"]


The ``ProtoDatasetModel`` and the ``DatasetModel`` models are used to work with dataset metadata.

.. code-block:: python

    >>> from dtool_gui import ProtoDatasetModel, DatasetModel
    >>> proto_dataset_model = ProtoDatasetModel()
    >>> proto_dataset_model.put_name("my-dataset")
    >>> proto_dataset_model.set_metadata_model(metadata_model)
    >>> proto_dataset_model.set_base_uri_model(base_uri_model)
    >>> proto_dataset_model.set_input_directory("/home/olssont/my_data")
    >>> if proto_dataset_model.metadata.is_okay():
    ...     proto_dataset_model.create()
    >>> dataset_model = DatasetModel()
    >>> dataset_model.put_uri(proto_dataset_model.uri)
    >>> print(dataset_model.get_name())
    "my-dataset"
    >>> dataset_model.put_name("new-name")
    >>> print(dataset_model.get_name())
    "new-name"

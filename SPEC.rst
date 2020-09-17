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

CHANGELOG
=========

This project uses `semantic versioning <http://semver.org/>`_.
This change log uses principles from `keep a changelog <http://keepachangelog.com/>`_.

[Unreleased]
------------


Added
^^^^^


Changed
^^^^^^^


Deprecated
^^^^^^^^^^


Removed
^^^^^^^


Fixed
^^^^^


Security
^^^^^^^^


[0.4.0] - 2021-02-24
--------------------

Improvements to make it easier to add metadata templates.

Added
^^^^^

- Added "File >> Import metadata template..."
- Added "file >> Export metadata template..."
- Added ``put_metadata_schema_item`` method to
  ``dtool_gui_tk.models.MetadataSchemaListModel``

Fixed
^^^^^

- Fixed defect where text entered into a metadata form could be lost
  when adding another optional metadata field;
  https://github.com/jic-dtool/dtool-gui-tk/issues/27


[0.3.1] - 2021-02-02
--------------------

Fixed
^^^^^

- Fixed issue where trying to edit tags for datasets with complex metadata raised errors;
  issue: https://github.com/jic-dtool/dtool-gui-tk/issues/23
- Fixed issue where tags in drop down filter did not update when tags where added or
  deleted; and when the local base URI directory was updated;
  issue: https://github.com/jic-dtool/dtool-gui-tk/issues/24
- Fixed issue when trying to sort a ``DataSetListModel`` with no datasets in it;
  issue: https://github.com/jic-dtool/dtool-gui-tk/issues/25


[0.3.0] - 2021-01-30
--------------------

Added
^^^^^

- Added ability to view, add and delete dataset tags
- Added ability to filter dataset list view by tag

Fixed
^^^^^

- Fixed defect where app crashed if there were no datasets present in the local
  base URI
- Fixed defect where it was impossible to open the Preferences dialogue if a
  local base URI had not already been configured
- Fixed defect where quit menu item and shortcut did not quit the application


[0.2.0] - 2020-12-22
--------------------

Added
^^^^^

- Added UI for updating metadata of an existing dataset
- Ability to sort datasets by DataSetListModel column headers
- Added display of dataset item relpaths and sizes of the active dataset
- Added dtool_gui_tk.models.DataSetListModel.get_active_name
- Added dtool_gui_tk.models.DataSetListModel.get_active_name method
- Added dtool_gui_tk.models.DataSetModel.get_item_props_list method


Changed
^^^^^^^

- Redesigned code to make dtool_gui_tk.models.DataSetListModel responsible for
  keeping track of the active index
- Stripped logic of updating the selected dataset in the DatsSetListFrame
  out of the event handler
- Renamed dtool_gui_tk.models.DataSetListModel.get_uri to get_active_uri


Fixed
^^^^^

- Fixed styling issues on Mac
- Improved UX of Preferences window
- Improved clarity of difference between local base URI and input data directory
- Prevent multiple copies of Preferences and Edit Metadata dialogues opening at once
- Improved resizing behaviour of NewDataSet window
- Various improvements to the UX


[0.1.1] - 2020-11-19
--------------------

Fixed
^^^^^

- Added dependencies to setup.py
- Add __version__ to __init__.py


[0.1.0] - 2020-11-19
--------------------

Initial release.

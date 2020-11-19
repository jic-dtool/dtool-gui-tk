from setuptools import setup

url = "https://github.com/jic-dtool/dtool-gui-tk"
version = "0.1.0"
readme = open('README.rst').read()

setup(
    name="dtool-gui-tk",
    packages=["dtool_gui_tk"],
    version=version,
    description="Graphical user interface for managing data using dtool",
    long_description=readme,
    include_package_data=True,
    author="Tjelvar Olsson",
    author_email="tjelvar.olsson@jic.ac.uk",
    url=url,
    install_requires=[
        "dtoolcore>=3.17.0",
        "jsonschema",
    ],
    entry_points={
        'console_scripts': ['dtool-tk=dtool_gui.tkgui:tkgui'],
    },
    download_url="{}/tarball/{}".format(url, version),
    license="MIT"
)

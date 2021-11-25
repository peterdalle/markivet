from setuptools import setup, find_packages


NAME = "Markivet"
VERSION = "0.5"
DESCRIPTION = "Converts Retriever Mediearkivet TXT files into structured data (JSON)."
URL = "https://github.com/peterdalle/markivet"
EXCLUDE_LIST = []
REQUIRED = ["python-dateutil"]

if __name__ == "__main__":
    setup(
        name=NAME,
        version=VERSION,
        packages=find_packages(exclude=EXCLUDE_LIST),
        description=DESCRIPTION,
        install_requires=REQUIRED,
        url=URL
    )

from glob import glob
from os.path import basename
from os.path import splitext
from setuptools import find_packages
from setuptools import setup
from src.caracara import __version__, __maintainer__, __title__, __description__, __author__
from src.caracara import __author_email__, __project_url__, __keywords__  # _DOCS_URL,

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name=__title__,
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    maintainer=__maintainer__,
    maintainer_email=__author_email__,
    # docs_url=_DOCS_URL,
    description=__description__,
    keywords=__keywords__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=__project_url__,
    project_urls={
        "Source": "https://github.com/CrowdStrike/caracara/tree/main/src/caracara",
        "Tracker": "https://github.com/CrowdStrike/caracara/issues"
    },
    # "Documentation": "https://www.falconpy.io",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    install_requires=[
        "crowdstrike-falconpy"
    ],
    extras_require={
        "dev": [
            "flake8",
            "coverage",
            "pylint",
            "pytest-cov",
            "pytest",
            "bandit",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: The Unlicense (Unlicense)",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities"
    ],
    python_requires='>=3.6',
)

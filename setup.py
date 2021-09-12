from glob import glob
from os.path import basename
from os.path import splitext
from setuptools import find_packages
from setuptools import setup
from src.falconpytools import _VERSION, _MAINTAINER, _TITLE, _DESCRIPTION, _AUTHOR
from src.falconpytools import _AUTHOR_EMAIL, _PROJECT_URL, _KEYWORDS  # _DOCS_URL,

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name=_TITLE,
    version=_VERSION,
    author=_AUTHOR,
    author_email=_AUTHOR_EMAIL,
    maintainer=_MAINTAINER,
    maintainer_email=_AUTHOR_EMAIL,
    # docs_url=_DOCS_URL,
    description=_DESCRIPTION,
    keywords=_KEYWORDS,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=_PROJECT_URL,
    project_urls={
        "Source": "https://github.com/CrowdStrike/falconpy-tools/tree/main/src/falconpytools",
        "Tracker": "https://github.com/CrowdStrike/falconpy-tools/issues"
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
        "Development Status :: 4 - Beta",
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

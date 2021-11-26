from glob import glob
from os.path import basename
from os.path import splitext
from setuptools import find_packages
from setuptools import setup

# This solution works for now, but it's not ideal.
# Direct importing will require setup to have crowdstrike-falconpy available.
meta_keys = [
    "_VERSION", "_MAINTAINER", "_TITLE", "_DESCRIPTION", "_AUTHOR",
    "_AUTHOR_EMAIL", "_PROJECT_URL", "_KEYWORDS"
]
meta = {}
with open("src/caracara/_version.py", "r") as ver:
    for line in ver:
        for metakey in meta_keys:
            if f"{metakey} " in line:
                metaval = line.rstrip().replace(f"{metakey} = ", "").replace("'", "")
                if metakey == "_KEYWORDS":
                    _ = metaval.replace("[", "").replace("]", "").replace('"', '')
                    meta[metakey] = _.split(", ")
                else:
                    meta[metakey] = metaval

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name=meta["_TITLE"],
    version=meta["_VERSION"],
    author=meta["_AUTHOR"],
    author_email=meta["_AUTHOR_EMAIL"],
    maintainer=meta["_MAINTAINER"],
    maintainer_email=meta["_AUTHOR_EMAIL"],
    # docs_url=_DOCS_URL,
    description=meta["_DESCRIPTION"],
    keywords=meta["_KEYWORDS"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=meta["_PROJECT_URL"],
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

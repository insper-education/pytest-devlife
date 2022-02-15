import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pytest-devlife",
    version="0.1.2",
    author="Andrew Kurauchi",
    author_email="andrewTNK@insper.edu.br",
    description="Pytest plugin for Insper Developer Life",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/insper-education/pytest-devlife",
    project_urls={
        "Bug Tracker": "https://github.com/insper-education/pytest-devlife/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL v2",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
    entry_points={
        'pytest11': [
            'devlife = pytest_devlife',
        ],
    },
)

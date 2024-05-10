from setuptools import setup, find_packages


__version__ = "0.0.1"

setup(
    name="form_flask",
    version=__version__,
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    package_data={'': ['*/*.yaml']},
    scripts=[],
    install_requires=[

    ],
)

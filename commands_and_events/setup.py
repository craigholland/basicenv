from setuptools import setup, find_packages


__version__ = "0.0.1"

setup(
    name="form_commands_and_events",
    version=__version__,
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    scripts=[],
    install_requires=[

    ],
)

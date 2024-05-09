from setuptools import setup, find_packages


__version__ = "0.0.2"

setup(
    name="form_domain",
    version=__version__,
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    package_data={'': ['*/*.yaml']},
    scripts=[],
    install_requires=[

    ],
)

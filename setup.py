from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

setup(
    name="mailping",
    version="0.0.1",
    description="Benachrichtigt bei mail über eingegangene Mail",
    long_description="Benachrichtigt bei mail über eingegangene Mail",
    author="Henryk Plötz",
    author_email="henryk+mailping@ploetzli.ch",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    install_requires=[
        "dynaconf[all]",
        "python-dotenv",
        "imapclient",
        "pysigset",
    ],
    extras_require={},
    package_data={},
    data_files=[],
    entry_points={"console_scripts": ["mailping=mailping:main.main",],},
)

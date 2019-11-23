from setuptools import setup

setup(
    name="magda_tools",
    version="0.1",
    description="A collection of tools for working with MAGDA data files",
    long_description="",
    url="https://github.com/ImperialCollege/magda_tools",
    author="Research Software Engineering Group, Imperial College",
    author_email="",
    packages=["magda_tools"],
    python_requires=">=3.6",
    install_requires=["astropy", "numpy", "sympy"],
    tests_require=["pytz"],
    project_urls={"Source": "https://github.com/ImperialCollege/magda_tools"},
)

from setuptools import setup

setup(
    name="magda_tools",
    version="0.1",
    description="A collection of tools for working with MAGDA data files",
    long_description="",
    url="https://github.com/ImperialCollege/magda_tools",
    author="Magnetometer Group, Imperial College",
    author_email="",
    packages=["magda_tools", "magda_tools.header_handler"],
    python_requires=">=3.6",
    install_requires=["astropy", "numpy", "pytz", "sympy"],
    project_urls={"Source": "https://github.com/ImperialCollege/magda_tools"},
    package_data={"magda_tools.header_handler": ["HeaderFileParser.jar"]},
)

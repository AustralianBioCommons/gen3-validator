from setuptools import setup, find_packages

setup(
    name="gen3_data_validator",  # Name of your package
    version="0.1",  # Version number
    packages=find_packages(where="src"),  # Automatically find packages in src/
    package_dir={"": "src"},  # Tell setuptools that packages are in src/
    install_requires=open("requirements.txt").read().splitlines(),  # Add dependencies from requirements.txt
    description="A library for validating data against Gen3 data schemas",
    author="Joshua Harris",
    author_email="harjo391@gmail.com",
    url="https://github.com/AustralianBioCommons/gen3-data-validator",  # Optional: GitHub or project URL
)
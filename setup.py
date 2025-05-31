from setuptools import find_packages, setup


def readme():
    with open('README.md', encoding='utf-8') as f:
        content = f.read()
    return content


def parse_requirements():
    with open("requirements.txt", "r") as f:
        return f.read().splitlines()


setup(
    name="omnisuite-examples",
    packages=find_packages(include=["omnisuite_examples"]),
    version='0.1.0',
    description='Example plot generation for use with OmniSuite',
    long_description=readme(),
    install_requires=parse_requirements(),
    author='See AUTHORS.md',
    author_email="frazier@iap-kborn",
    license='BSD-3-Clause'
)

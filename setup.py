from setuptools import setup, find_packages
setup(
    name="papercup",
    version="0.0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
                'papercup = papercup.main:main'
        ]
    }
)
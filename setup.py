from setuptools import setup, find_packages
setup(
    name="papercup",
    version="0.0.4",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
                'papercup = papercup.main:main'
        ]
    },
    package_data={
      'papercup': ['static/*', 'migrations/*']
    }
)

#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', ]

test_requirements = ['pytest>=3', ]

setup(
    author="Marek Pilch",
    author_email='marpi82@gmail.com',
    python_requires='>=3.9',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    description="Python library wrapping BragerConnect for home-assistant.",
    entry_points={
        'console_scripts': [
            'bragerconnect=bragerconnect.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='bragerconnect',
    name='bragerconnect',
    packages=find_packages(include=['bragerconnect', 'src.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/marpi82/py-bragerconnect',
    version='0.1.0',
    zip_safe=False,
)

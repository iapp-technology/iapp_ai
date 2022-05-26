#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ ]

test_requirements = ['pytest>=3', ]

setup(
    author="Kobkrit Viriyayudhakorn",
    author_email='kobkrit@iapp.co.th',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="iApp AI API pip package",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    # long_description_content_type="text/markdown",
    include_package_data=True,
    keywords='iapp_ai',
    name='iapp_ai',
    packages=find_packages(include=['iapp_ai', 'iapp_ai.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/iapp-technology/iapp_ai',
    version='1.0.0',
    zip_safe=False,
)

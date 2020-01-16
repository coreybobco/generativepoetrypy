from setuptools import setup, find_packages

__author__ = 'Corey Bobco'
__email__ = 'corey.bobco@gmail.com'
__version__ = '0.2.0'

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'hunspell>=0.5.5',
    'nltk==3.4.5',
    'pronouncing>=0.2.0',
    'python-datamuse==1.2.1',
    'unittest2==1.1.0',
    'wordfreq>=2.2.1',
    'console-menu==0.6.0',
]

setup(
    name='generativepoetry',
    version='0.2.0',
    description='A library primarily for procedurally generating visual poems',
    long_description=readme,
    author="Corey Bobco",
    author_email='corey.bobco@gmail.com',
    url='https://github.com/coreybobco/generativepoetry-py',
    packages=[
        'generativepoetry',
    ],
    package_dir={'generativepoetry':
                 'generativepoetry'},
    install_requires=requirements,
    license="MIT",
    zip_safe=True,
    keywords='poetry',
    classifiers=[
        "Development Status :: 3 - Alpha",
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Topic :: Artistic Software",
    ],
    test_suite='tests',
)

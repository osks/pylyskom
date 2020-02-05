import setuptools

from pylyskom.version import __version__


with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pylyskom',
    version=__version__,
    description='Python LysKOM library',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author='Oskar Skoog',
    author_email='oskar@osd.se',
    url='https://github.com/osks/pylyskom',
    packages=['pylyskom'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'six',
    ]
)

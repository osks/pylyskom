import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pylyskom',
    version='0.2',
    description='Python LysKOM library',
    long_description=long_description,
    long_description_content_type="text/markdown",
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
    #python_requires='>=2.7, >=3.7',
    install_requires=[
        'six',
    ]
)

from setuptools import setup

setup(name='pylyskom',
      version='0.1.0',
      description='Python LysKOM library',
      packages=['pylyskom'],
      author='Oskar Skoog',
      author_email='oskar@osd.se',
      url='https://github.com/osks/pylyskom',
      # pylyskom is egg safe. But we hate eggs
      zip_safe=False,
      classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      )

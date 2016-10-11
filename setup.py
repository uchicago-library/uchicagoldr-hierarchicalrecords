from setuptools import setup, find_packages

setup(
    name = 'hierarchicalrecord',
    version = '1.0.0',
    author = "Brian Balsamo",
    author_email = ["balsamo@uchicago.edu"],
    packages = find_packages(
        exclude = [
            "build",
            "dist",
            "docs",
            "hierarchicalrecord.egg-info"
        ]
    ),
    description = "A library providing easy access to a hierarchical record data organization",
    keywords = ["uchicago","repository","records"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Operating System :: Unix",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    entry_points = {
        'console_scripts':[
            'validatehr = hierarchicalrecord.bin.validaterecord:main'
        ]
    }
    )

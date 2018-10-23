import setuptools

with open("README.md", "r") as fh:

    long_description = fh.read()

setuptools.setup(

    name='BIP',

    version='1.0',

    scripts=['bip.py'],

    author="Reed Haffner",

    author_email="reedhaffner@pm.me",

    description="Binary In Picture",

    long_description=long_description,

    url="https://github.com/reedhaffner/BIP",

    packages=setuptools.find_packages(),

    classifiers=[

        "Programming Language :: Python :: 3",

        "License :: OSI Approved :: GPLv3 License",

        "Operating System :: OS Independent",

    ],

    install_requires=[
        'Click',
    ],

    entry_points='''
        [console_scripts]
        bip=bip:bip
    ''',


)

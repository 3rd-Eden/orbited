#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from setuptools import setup

setup(
    name = 'jsnap_trac_theme',
    version = '1.0',
    packages = ['jsnap_trac_theme'],
    package_data = { 'jsnap_trac_theme': [
        'templates/*.html',
        'htdocs/*.png',
        'htdocs/*.css'
        ] 
    },

    author = 'Frank Salim',
    author_email = 'frank.salim@gmail.com',
    description = 'Theme for the JSNAP website',
    license = 'MIT',
    keywords = 'trac plugin theme',
    url = 'http://jsnap.orbited.org',
    classifiers = [
        'Framework :: Trac',
    ],
    
    install_requires = ['Trac', 'TracThemeEngine>=2.0'],

    entry_points = {
        'trac.plugins': [
            'jsnap_trac_theme.theme = jsnap_trac_theme.theme',
        ]
    },
)

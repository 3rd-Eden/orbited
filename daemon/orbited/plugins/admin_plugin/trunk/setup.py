from setuptools import setup, find_packages
import os
static_types = [
    '*.js',
    '*.html',
    '*.css',
    '*.ico',
    '*.gif',
    '*.jpg',
    '*.png',
    '*.bmp',
    '*.txt*',
]

setup(
    name='admin',
    version='0.1.0',
    author='Frank Salim, Mario Balibrera',
    author_email='frank.salim@gmail.com; mario.balibrera@gmail.com',
    license='MIT',
    description='Admin Plugin',
    long_description='',
    packages=[
	"admin"
    ],
    package_data = {
        '': reduce(list.__add__, [ '.svn' not in d and [ os.path.join(d[6:], e) for e in static_types ] or [] for (d, s, f) in os.walk(os.path.join('admin', 'static')) ])
    },
    zip_safe = False,
    install_requires = [
        "orbited >= 0.2",
    ],

    entry_points = '''    
        
        [orbited.plugins]
        admin = admin.main:AdminPlugin
        
    ''',
        
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],        
)

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
    '*.txt*',
]

setup(
    name='orbited',
    version='0.4.0.twisted',
    author='Michael Carter',
    author_email='CarterMichael@gmail.com',
    url='http://www.orbited.org',
    download_url='http://www.orbited.org/download',
    license='MIT License',
    description='A twisted-based comet server',
    long_description='',
    packages=[
        'orbited', 
        'orbited.network',         
    ],
    package_data = {
        '': [os.path.join('static', ext) for ext in static_types],
    },
    zip_safe = False,
    install_requires = [
        # "event >= 0.3"
    ],
    
    entry_points = '''    
        [console_scripts]
        orbited = orbited.start:main
    ''',
    
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],        
)

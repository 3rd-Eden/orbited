#from ez_setup import use_setuptools
#use_setuptools()
from setuptools import setup
setup(
    name='orbited',
    version='0.1.6',
    author='Michael Carter',
    author_email='CarterMichael@gmail.com',
    url='http://orbited.org',
    download_url='http://orbited.org/download',
    license="MIT License",
    description='A libevent/pyevent based comet server',
    long_description='',    
    packages=["orbited"],    
    
    install_requires = [
#        "event >= 0.3"
    ],
    
    entry_points = """
    
    [console_scripts]
    orbited = orbited.start:main
        
    """,

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'],        
    )
    
    
    
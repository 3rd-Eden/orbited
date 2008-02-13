from setuptools import setup, find_packages
import os

setup(
    name='rel',
    version='0.1.0',
    author='Mario Balibrera',
    author_email='mario.balibrera@gmail.com',
    license='MIT License',
    description='Registered Event Listener. Provides standard (pyevent) interface and functionality for systems that support: pyevent,epoll,kqueue,select,poll.',
    long_description='Select preferred event notification methods with initialize([methods in order of preference]). If initialize(...) is not called, methods are tried in default order: pyevent,epoll,kqueue,select,poll.',
    packages=[
        'rel',
    ],
    zip_safe = False,
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
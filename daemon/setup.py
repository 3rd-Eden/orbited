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
    version='0.4.0',
    author='Michael Carter',
    author_email='CarterMichael@gmail.com',
    url='http://www.orbited.org',
    download_url='http://www.orbited.org/download',
    license='MIT License',
    description='A libevent/pyevent based comet server',
    long_description='',
    packages=[
        'dez',
        'orbited', 
#        'orbited.http',
        'orbited.logger',         
#        'orbited.op',
#        'orbited.stomp',
#        'orbited.transports',
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
        orbited_profile = orbited.start:profile
        orbited_daemonized = orbited.start:daemon
        dez_test = dez.test:main
        dez_test_profile = dez.test:profile
          
#        [orbited.transports]
#        raw = orbited.transports.raw:RawTransport
#        basic = orbited.transports.basic:BasicTransport
#        stream = orbited.transports.stream:StreamTransport
#        iframe = orbited.transports.iframe:IFrameTransport
#        xhr_multipart = orbited.transports.xhr_multipart:XHRMultipartTransport
#        xhr_stream = orbited.transports.xhr_stream:XHRStreamTransport
#        server_sent_events = orbited.transports.sse:ServerSentEventsTransport
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

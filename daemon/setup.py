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
    packages= find_packages(),
    package_data = {'': reduce(list.__add__, [ '.svn' not in d and [ os.path.join(d[len('orbited')+1:], e) for e in
            static_types ] or [] for (d, s, f) in os.walk(os.path.join('orbited', 'static'))
        ]) },
    zip_safe = False,
    install_requires = [
        # "event >= 0.3"
    ],
    
    entry_points = '''    
        [console_scripts]
        orbited = orbited.start:main
        orbited_profile = orbited.start:profile
        orbited_daemonized = orbited.start:daemon
          
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

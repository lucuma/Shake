# -*- coding: utf-8 -*-
from setuptools import setup


def run_tests():
    import sys, subprocess
    errno = subprocess.call([sys.executable, 'runtests.py'])
    raise SystemExit(errno)


setup(
    name='Shake',
    version='0.5dev',
    author='Juan-Pablo Scaletti',
    author_email='juanpablo@lucumalabs.com',
    packages=['shake'],

    url='http://github.com/lucuma/Shake',
    license='BSD',
    description='A web framework mixed from the best ingredients',
    long_description=open('README.txt').read(),
    include_package_data=True,
    install_requires=[
        'Werkzeug>=0.6.1',
        'Jinja2>=2.4'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite='__main__.run_tests'
)

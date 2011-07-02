"""
Shake
-----

A web framework mixed from the best ingredients

Easy to use
`````````````````
::
    from shake import Shake, Rule

    def hello():
        return 'Hello World!'
    
    urls = [
        Rule('/', hello),
        ]
    app = Shake(urls)

    if __name__ == "__main__":
        app.run()


And easy to set up
```````````````````
::
    $ pip install Shake
    $ python hello.py
     * Running on http://localhost:5000/

"""
try:
    from setuptools.core import setup, Command
except ImportError:
    from distutils.core import setup, Command


class run_audit(Command):
    """Audits source code using PyFlakes for following issues:
        - Names which are used but not defined or used before they are defined.
        - Names which are redefined without having been used.
    """
    description = "Audit source code with PyFlakes"
    user_options = []

    def initialize_options(self):
        all = None

    def finalize_options(self):
        pass

    def run(self):
        import os, sys
        try:
            import pyflakes.scripts.pyflakes as flakes
        except ImportError:
            print "Audit requires PyFlakes installed in your system."""
            sys.exit(-1)

        dirs = ['shake', 'tests']
        warns = 0
        for dir in dirs:
            for filename in os.listdir(dir):
                if filename.endswith('.py') and filename != '__init__.py':
                    warns += flakes.checkPath(os.path.join(dir, filename))
        if warns > 0:
            print ("Audit finished with total %d warnings." % warns)
        else:
            print ("No problems found in sourcecode.")


def run_tests():
    import sys, subprocess
    errno = subprocess.call([sys.executable, 'runtest.py'])
    raise SystemExit(errno)


setup(
    name='Shake',
    version='0.5-dev',
    url='http://github.com/lucuma/Shake',
    license='BSD',
    author='Juan-Pablo Scaletti',
    author_email='juanpablo@lucumalabs.com',
    description='A web framework mixed from the best ingredients',
    long_description=__doc__,
    packages=['shake'],
    zip_safe=False,
    platforms='any',
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
    cmdclass={'audit': run_audit},
    test_suite='__main__.run_tests'
)

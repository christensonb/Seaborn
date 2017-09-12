from setuptools import setup, find_packages

plugins = []
setup(
    name='seaborn',
    version='0.2.1',
    description='This contains a lot of helper wrapper modules and other libraries',
    long_description='',
    author='Ben Christenson',
    author_email='Python@BenChristenson.com',
    url='',
    install_requires=["Flask>=0.11.1", "Flask-DebugToolbar==0.10.0", "Flask-Login>=0.3.2", "Flask-Migrate>=2.0.0",
                      "Flask-Script==2.0.5", "Flask-SQLAlchemy>=2.1", "Flask-Testing>=0.6.1", "Flask-WTF>=0.13.1",
                      "gevent>=1.1.2", "greenlet>=0.4.10", "markupSafe==0.23", "requests>=2.11.1", "simplejson>=3.8.2",
                      "six>=1.10.0", "SQLAlchemy>=1.1.1", "test-chain>=0.0.1", "Werkzeug>=0.11.11", "WTForms>=2.1",
                      "psycopg2>=2.7.1",],
    packages=find_packages(exclude=()),
    license='MIT License',
    classifiers=(
        'Development Status :: 1 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: Other/Proprietary License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5'))

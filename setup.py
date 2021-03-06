from setuptools import find_packages, setup

docs_require = [
    'sphinx>=2.0.1',
]

tests_require = [
    'coverage==4.5.3',
    'pytest==4.4.1',
    'pytest-django==3.4.8',
    'requests-mock==1.5.2',
    'freezegun==0.3.11',

    # Linting
    'isort==4.2.5',
    'flake8==3.0.3',
    'flake8-blind-except==0.1.1',
    'flake8-debugger==1.4.0',
]

setup(
    name='django-healthchecks',
    version='1.4.2',
    description="Simple Django app/framework to publish health checks",
    long_description=open('README.rst', 'r').read(),
    url='https://github.com/mvantellingen/django-healthchecks',
    author="Michael van Tellingen",
    author_email="michaelvantellingen@gmail.com",
    install_requires=[
        'Django>=1.11',
        'six>=1.1',
        'requests>=2.21.0',
        'certifi>=2019.3.9',
    ],
    tests_require=tests_require,
    extras_require={
        'docs': docs_require,
        'test': tests_require,
    },
    use_scm_version=True,
    entry_points={},
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    zip_safe=False,
)

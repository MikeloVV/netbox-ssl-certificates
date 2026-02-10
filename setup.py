from setuptools import find_packages, setup

setup(
    name='netbox-ssl-certificates',
    version='1.0.4',
    description='SSL Certificate management plugin for NetBox',
    author='Mikhail Voronov',
    author_email='mikhail.voronov@gmail.com',
    license='Apache 2.0',
    install_requires=[
        'cryptography>=41.0.0',
    ],
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['migrations/*.py', 'templates/**/*.html', 'static/**/*'],
    },
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


readme = open('README.md').read()


def get_version():
    import imp

    source_dir = 'dqc_us_rules'

    with open('{}/_pkg_meta.py'.format(source_dir), 'rb') as fp:
        mod = imp.load_source('_pkg_meta', source_dir, fp)

    return mod.version


setup_args = dict(
    name='dqc_us_rules',
    version=get_version(),
    description="""""".strip(),
    long_description=readme,
    maintainer='Data Quality Committee',
    maintainer_email='dqc@xbrl.us',
    url='https://github.com/DataQualityCommittee/dqc_us_rules',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        "Topic :: Office/Business :: Financial :: Accounting"
    ],
    test_suite='test',
    install_requires=[],
    tests_require=[
        "lxml==2.3.5",
        "nose==1.3.4",
        "mock==1.0.1",
        "arelle"
    ],
)


if __name__ == '__main__':
    setup(**setup_args)

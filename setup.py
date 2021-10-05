from distutils.core import setup

setup(
    name='entity_search_engines',
    packages=['entity_search_engines'],
    version='0.1.1',
    description='Entity search engines for Google and Wikidata.  Helping to link the two together and provide a way to ground entities',
    author='Michael Doran',
    author_email='mikrdoran@gmail.com',
    url='https://github.com/miksyr/entity_search_engines',
    download_url='https://github.com/miksyr/entity_search_engines/archive/v_01.tar.gz',
    keywords=['google knowledge graph', 'wikidata', 'entity grounding', 'entity management'],
    install_requires=[
            'requests>=2.24.0',
            'numpy>=1.19.1',
            'tqdm>=4.38.0'
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)

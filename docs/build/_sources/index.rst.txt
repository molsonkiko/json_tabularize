.. json_tabularize documentation master file, created by
   sphinx-quickstart on Fri Oct  1 10:14:51 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. to build this as HTML, use the terminal, go to json_tabularize's directory, and enter
   sphinx-build -b html json_tabularize/docs/source json_tabularize/docs/build/html
   
.. 80 characters is the recommended maximum line length for reST.

Welcome to json_tabularize's documentation!
=============================================
**Get arbitrarily nested JSON into tabular format**

This is a tool for converting many different JSON formats into tabular JSON. You can then use other tools to turn those into nice things like HTML, CSV, etc.

Here's a motivating example of where to use this::

	>>> bball = {'leagues': [
		{
		'league': 'American',
		'teams': [
				{
					'name': 'foo',
					'players': [
						{'name': 'alice', 'hits': [1], 'at-bats': [3]},
					]
				},
				{
					'name': 'bar',
					'players': [
						{'name': 'carol', 'hits': [1], 'at-bats': [2]}
					]
				}
			],
		},
		{
		'league': 'National',
		'teams': [
				{
					'name': 'baz',
					'players': [
						{'name': 'bob', 'hits': [2], 'at-bats': [3]}
					]
				}
			]
		}
	]}


This JSON has a regular structure, and it would be reasonable to try converting this into a table. However, algorithms like `normalize_json` from `pandas <https://pandas.pydata.org/>`_ can't fully normalize it, but rather puts everything in one row::

	>>> import pandas as pd
	>>> pd.json_normalize(bball, ['leagues', 'teams', 'players'])
		name hits at-bats
	0  alice  [1]     [3]
	1  carol  [1]     [2]
	2    bob  [2]     [3]


This is pretty good, but it results in loss of information, and you have to spend some time troubleshooting and reading the documentation to be able to use it.

Let's try using my algorithm::

	>>> pd.DataFrame(build_tab(bball))
	  leagues.teams.players.name leagues.league leagues.teams.name  leagues.teams.players.hits  leagues.teams.players.at-bats
	0                      alice       American                foo                           1                              3
	1                      carol       American                bar                           1                              2
	2                        bob       National                baz                           2                              3


All the information has been retained. Note that pandas is NOT a dependency of this package.

Another advantage of this algorithm is that it recognizes all of the following formats as tables::


	>>> {'a': [1, 2], 'b': ['a', 'b']} # this is a table
	>>> [{'a': 1, 'b': 'a'}, {'a': 2, 'b': 'b'}] # also a table
	>>> [[1, 'a'], [2, 'b']] # yep, still a table


The program infers table formats without user input.

Limitations:
	1. This algorithm only works on JSON that has one or fewer possible tables within it.
	2. All arrays must be lists.
	3. This won't recognize a single flat list or dict as a table.
	4. You must have `GenSON <https://github.com/wolverdude/GenSON>`_ installed.

In conclusion, you should still use pandas for the 95+% of "tabularizable" real-world JSON that can be fully normalized into a table by `pandas.read_json` or `pandas.json_normalize`, but this package exists for those other rare cases.

.. note:: This project is under active development.
    
    Features to be added soon:
    
		1. Tools for getting more than one table out of the same JSON document.
		2. Tools for converting the tabular JSON directly into other formats.

Table of Contents
==================

.. toctree::
   :maxdepth: 2
   
   installation
   command line

.. the ".." precedes a comment
   this is in the same comment block (because of indentation)
   the first dedented line after the beginning of the block marks the end of the block

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

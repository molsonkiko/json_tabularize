json_tabularize
============

*Get arbitrarily nested JSON into tabular format*

[Read the Docs] (https://json_tabularize.readthedocs.io/en/latest/index.html)


Features
--------

* Convert deeply nested JSON into tabular format.
* Easy to use; the build_tab function only requires one argument to parse any JSON that contain some tabular or "tabularizable" JSON.
* Recognize multiple formats that can be converted into tables.
* CLI tool for outputting the tabular JSON as JSON.

How to use
----------

* Install Python 3.6 or newer.
* Install

    ```sh
    # or PyPI
    pip install json_tabularize
    ```

Here's a motivating example of where to use this:
```{py}
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
```

This JSON has a regular structure, and it would be reasonable to try converting this into a table. However, algorithms like pandas' normalize_json can't fully normalize it, but rather puts everything in one row.

```{py}
>>> import pandas as pd
>>> pd.json_normalize(bball, ['leagues', 'teams', 'players'])
    name hits at-bats
0  alice  [1]     [3]
1  carol  [1]     [2]
2    bob  [2]     [3]
```

This is pretty good, but it results in loss of information, and you have to spend some time troubleshooting and reading the documentation to be able to use it.

Let's try using my algorithm.

```{py}
>>> pd.DataFrame(build_tab(bball))
  leagues.teams.players.name leagues.league leagues.teams.name  leagues.teams.players.hits  leagues.teams.players.at-bats
0                      alice       American                foo                           1                              3
1                      carol       American                bar                           1                              2
2                        bob       National                baz                           2                              3
```

All the information has been retained. Note that pandas is NOT a dependency of this package.

Another advantage of this algorithm is that it recognizes all of the following formats as tables:

```{py}
>>> {'a': [1, 2], 'b': ['a', 'b']} # this is a table
>>> [{'a': 1, 'b': 'a'}, {'a': 2, 'b': 'b'}] # also a table
>>> [[1, 'a'], [2, 'b']] # yep, still a table
```

The program infers table formats without user input.

Limitations:
1. This algorithm only works on JSON that has one or fewer possible tables within it.
2. All arrays must be lists.
3. This won't recognize a single flat list or dict as a table.
4. You must have [GenSON](https://github.com/wolverdude/GenSON) installed.

In conclusion, you should still use pandas for the 95+% of "tabularizable" real-world JSON that can be fully normalized into a table by read_json or json_normalize, but this package exists for those other rare cases.

Contributing
------------

Be sure to read the [contribution guidelines](https://github.com/molsonkiko/json_tabularize/blob/main/CONTRIBUTING.md).
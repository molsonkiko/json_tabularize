=============
command line
=============

json_tabularize is most conveniently used from the command line. You can run the package directly like so::

	C:/Users/mjols/Python39> more baseball2.json
	[
        {"name": "foo",
        "players":
                [
                        {"name": "alice",
                        "hits": [3, 4, 2, 5],
                        "at-bats": [4, 3, 3, 6]},
                        {"name": "bob",
                        "hits": [-2, 0, 4, 6],
                        "at-bats": [1, 3, 5, 6]}
                ]
        },
        {"name": "bar",
        "players":
                [
                        {"name": "carol",
                        "hits": [7, 3, 0, 5],
                        "at-bats": [8, 4, 6, 6]},
                        {"name": "dave",
                        "hits": [1, 0, 4, 10],
                        "at-bats": [1, 3, 6, 11]}
                ]
        }
	]
	
    C:/Users/mjols/Python39> python -m json_tabularize baseball2.json	
	[
		{
			"players.name": "alice",
			"name": "foo",
			"players.hits": 3,
			"players.at-bats": 4
		},
		{
			"players.name": "alice",
			"name": "foo",
			"players.hits": 4,
			"players.at-bats": 3
		},
		{
			"players.name": "alice",
			"name": "foo",
			"players.hits": 2,
			"players.at-bats": 3
		},
		{
			"players.name": "alice",
			"name": "foo",
			"players.hits": 5,
			"players.at-bats": 6
		},
		{
			"players.name": "bob",
			"name": "foo",
			"players.hits": -2,
			"players.at-bats": 1
		},
		{
			"players.name": "bob",
			"name": "foo",
			"players.hits": 0,
			"players.at-bats": 3
		},
		{
			"players.name": "bob",
			"name": "foo",
			"players.hits": 4,
			"players.at-bats": 5
		},
		{
			"players.name": "bob",
			"name": "foo",
			"players.hits": 6,
			"players.at-bats": 6
		},
		{
			"players.name": "carol",
			"name": "bar",
			"players.hits": 7,
			"players.at-bats": 8
		},
		{
			"players.name": "carol",
			"name": "bar",
			"players.hits": 3,
			"players.at-bats": 4
		},
		{
			"players.name": "carol",
			"name": "bar",
			"players.hits": 0,
			"players.at-bats": 6
		},
		{
			"players.name": "carol",
			"name": "bar",
			"players.hits": 5,
			"players.at-bats": 6
		},
		{
			"players.name": "dave",
			"name": "bar",
			"players.hits": 1,
			"players.at-bats": 1
		},
		{
			"players.name": "dave",
			"name": "bar",
			"players.hits": 0,
			"players.at-bats": 3
		},
		{
			"players.name": "dave",
			"name": "bar",
			"players.hits": 4,
			"players.at-bats": 6
		},
		{
			"players.name": "dave",
			"name": "bar",
			"players.hits": 10,
			"players.at-bats": 11
		}
	]
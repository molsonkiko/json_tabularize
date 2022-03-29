from json_tabularize.tabularize import *
import unittest

baseball2 = [
    {"name": "foo",
    "players": [
        {"name": "alice",
            "hits": [3, 4, 2, 5], "at-bats": [4, 3, 3, 6]},
        {"name": "bob",
            "hits": [-2, 0, 4, 6], "at-bats": [1, 3, 5, 6]}
        ]
    },
    {"name": "bar",
    "players": [
        {"name": "carol",
            "hits": [7, 3, 0, 5], "at-bats": [8, 4, 6, 6]},
        {"name": "dave",
            "hits": [1, 0, 4, 10], "at-bats": [1, 3, 6, 11]}
        ]
    }
]

counties = [{"state": "Florida",
  "shortname": "FL",
  "info": {"governor": "Rick Scott"},
  "counties": [{"name": "Dade", "population": 12345},
   {"name": "Broward", "population": 40000},
   {"name": "Palm Beach", "population": 60000}]},
 {"state": "Ohio",
  "shortname": "OH",
  "info": {"governor": "John Kasich"},
  "counties": [{"name": "Summit", "population": 1234},
   {"name": "Cuyahoga", "population": 1337}]}]

bad_json = {"a": False, "b": "3", "6": 7, "9": "ball", "jub": {"uy": [1, 2, float('nan')], "yu": [[6, {"y": "b", "m8": 9}], None], "status": "jubar"}, "9\"a\"": 2, "blutentharst": ["\\n\'\"DOOM\" BOOM, AND I CONSUME\', said Bludd, the mighty Blood God.\\n\\t", True]}


def test_schema_class_right(tester, classification, obj):
    '''get the schema for the object, and see if classify_schema classifies
    the schema correctly'''
    schema = get_schema(obj)
    tester.assertEqual(classification, classify_schema(schema))


def test_find_tabs_right(tester, tab_locs, obj):
    schema = get_schema(obj)
    tester.assertEqual(tab_locs, find_tabs_in_schema(schema))


class BuildSchemaTests(unittest.TestCase):
    def test_genson(self):
        builder = SchemaBuilder()
        builder.add_object({'foo': 1, 'bar': [2, 3]})
        builder.add_object({'foo': 1, 'baz': 'a'})
        builder.to_schema()
        {'$schema': 'http://json-schema.org/schema#', 'type': 'object', 'properties': {'foo': {'type': 'integer'}, 'bar': {'type': 'array', 'items': {'type': 'integer'}}, 'baz': {'type': 'string'}}, 'required': ['foo']}
        # note that it's better practice to use https://json-schema.org/draft/<latest release date>/schema as the '$schema' value

    def test_classify_schema_scal(self):
        for scal in [1, 2., '3', None, True]:
            with self.subTest(scal=scal):
                test_schema_class_right(self, 'scal', scal)

    def test_classify_schema_list_int(self):
        test_schema_class_right(self, 'row', [1, 2, 3])

    def test_classify_schema_list_mixed_scalars(self):
        test_schema_class_right(self, 'row', [1, None, 2.4])

    def test_classify_schema_list_mixed_bad(self):
        test_schema_class_right(self, 'bad', [1, [1, 2]])

    def test_classify_schema_list_list_scals(self):
        test_schema_class_right(self, 'sqr', [['a', 1], ['c', 2]])

    def test_classify_schema_list_list_float(self):
        test_schema_class_right(self, 'sqr', [[1.0, 2.0], [3.0, 4.0]])

    def test_classify_schema_list_list_bad(self):
        test_schema_class_right(self, 'bad', [[[], 1], [2, 3]])

    def test_classify_schema_list_obj_scal(self):
        test_schema_class_right(self, 'rec', [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}])

    def test_classify_schema_list_obj_bad(self):
        test_schema_class_right(self, 'bad', [{'a': [], 'b': 2, 'c': 3}])

    def test_classify_schema_obj_scal(self):
        test_schema_class_right(self, 'row', {'a': 1, 'b': 2., 'c': 'a', 'd': False})

    def test_classify_schema_obj_list_scal(self):
        test_schema_class_right(self, 'tab', {'a': [1, 2], 'b': ['a', 'b']})

    def test_classify_schema_obj_scal_list_scal(self):
        test_schema_class_right(self, 'tab', {'a': 'foo', 'b': [1], 'b': ['a']})

    def test_classify_schema_obj_obj(self):
        test_schema_class_right(self, 'bad', {'a': {'b': 1, 'c': [2]}})

    def test_classify_schema_obj_all_scal_obj(self):
        test_schema_class_right(self, 'row', {'a': {'b': 1, 'c': 2}})

    def test_classify_schema_obj_mixed_scal_list_scal(self):
        builder = SchemaBuilder()
        builder.add_object({'a': 1, 'b': 2, 'c': [1, 2]})
        builder.add_object({'a': 2.0, 'b': 3, 'c': [3, 4]})
        schema = builder.to_schema()
        self.assertEqual('tab', classify_schema(schema))

    def test_classify_schema_obj_mixed_scal(self):
        builder = SchemaBuilder()
        builder.add_object({'a': 1, 'b': 2})
        builder.add_object({'a': 2.0, 'b': 3})
        schema = builder.to_schema()
        self.assertEqual('row', classify_schema(schema))

    def test_classify_schema_obj_mixed_obj(self):
        test_schema_class_right(self, 'bad', {'a': 1, 'b': [1, 2], 'c': {'d': [3]}})

    def test_classify_schema_obj_list_mixed_scal(self):
        test_schema_class_right(self, 'tab', {'a': [1, 2], 'b': [3, '4']})

    def test_classify_schema_obj_list_mixed_bad(self):
        test_schema_class_right(self, 'bad', {'a': [1, 2], 'b': [3, ['4']]})

    ##############
    ## find_tabs_in_schema tests
    ##############

    def test_find_tabs_scal(self):
        for scal in [1, 2., '3', None, True]:
            with self.subTest(scal=scal):
                test_find_tabs_right(self, {}, scal)

    def test_find_tabs_row(self):
        for row in [[1,2], [1.0, None], {'a': 1, 'b': 'c'}, {'a': 1, 'b': 2}]:
            with self.subTest(row=row):
                test_find_tabs_right(self, {}, row)

    def test_find_tabs_rec(self):
        test_find_tabs_right(self, {(): 'rec'}, [{'a': 1, 'b': 'c'}, {'a': 2, 'b': 'd'}, {'a': 'e', 'b': 'f'}])

    def test_find_tabs_sqr(self):
        for square in [
            [[1.0, 2.0], [3.0, 4.0]],
            [[1, '2'], ['3', 4]]
        ]:
            with self.subTest(square=square):
                test_find_tabs_right(self, {(): 'sqr'}, square)

    def test_find_tabs_tab(self):
        for tab in [
            {'a': [1, 2], 'b': ['3', 4]},
            {'a': [True, False], 'b': [None, 3.0], 'c': 'blah'},
            {'a': [1, 2], 'b': 3.4, 'c': 'blah'},
        ]:
            with self.subTest(tab=tab):
                test_find_tabs_right(self, {(): 'tab'}, tab)

    def test_find_tabs_tab_mixed_scal(self):
        obj = [{'a': [1, 2], 'b': 3.4, 'c': 'd', 'e': ['a', 'b']},
               {'a': [1, 2], 'b': "3.4", 'c': 'd', 'e': ['a', 'b']}
              ]
        test_find_tabs_right(self, {(inf,): 'tab'}, obj)

    def test_find_tabs_bad(self):
        test_find_tabs_right(self, {}, bad_json)

    def test_find_tab_pendant_all_scal_obj(self):
        obj = {'a': {'b': 'c'}, 'd': 1, 'e': [2., 3.]}
        test_find_tabs_right(self, {(): 'tab'}, obj)
        
    ###########
    ## anytable_to_record tests
    ###########
    
    def test_anytable_to_record_sqr_float(self):
        sqr = [[1.0, 2.0], [3.0, 4.0]]
        correct_out = [{'col1': 1.0, 'col2': 2.0}, {'col1': 3.0, 'col2': 4.0}]
        self.assertEqual(correct_out, anytable_to_record(sqr, 'sqr'))
        
    def test_anytable_to_record_sqr_mixed(self):
        sqr = [[1, '2'], ['3', 4]]
        correct_out = [{'col1': 1, 'col2': '2'}, {'col1': '3', 'col2': 4}]
        self.assertEqual(correct_out, anytable_to_record(sqr, 'sqr'))
        
    def test_anytable_to_record_sqr_extra(self):
        sqr = [[1.0, 2.0], [3.0, 4.0]]
        extra = {'a': 'b'}
        correct_out = [{'a': 'b', 'col1': 1.0, 'col2': 2.0}, {'a': 'b', 'col1': 3.0, 'col2': 4.0}]
        self.assertEqual(correct_out, anytable_to_record(sqr, 'sqr', extra))
                                                        
    def test_anytable_to_record_tab(self):
        tab = {'a': [1, 2], 'b': ['a', 'b']}
        correct_out = [{'a': 1, 'b': 'a'}, {'a': 2, 'b': 'b'}]
        self.assertEqual(correct_out, anytable_to_record(tab, 'tab'))
        
    def test_anytable_to_record_tab_extra(self):
        tab = {'a': [1, 2], 'b': ['a', 'b']}
        extra = {'c': 'd'}
        correct_out = [{'a': 1, 'b': 'a', 'c': 'd'}, {'a': 2, 'b': 'b', 'c': 'd'}]
        self.assertEqual(correct_out, anytable_to_record(tab, 'tab', extra))
       
    def test_anytable_to_record_tab_scal(self):
        tab = {'a': [1, 2], 'b': ['a', 'b'], 'c': 'd'}
        correct_out = [{'a': 1, 'b': 'a', 'c': 'd'}, {'a': 2, 'b': 'b', 'c': 'd'}]
        self.assertEqual(correct_out, anytable_to_record(tab, 'tab'))
        
    def test_anytable_to_record_tab_scal_extra(self):
        tab = {'a': [1, 2], 'b': ['a', 'b'], 'c': 'd'}
        extra = {'e': 'f'}
        correct_out = [{'a': 1, 'b': 'a', 'c': 'd', 'e': 'f'}, {'a': 2, 'b': 'b', 'c': 'd', 'e': 'f'}]
        self.assertEqual(correct_out, anytable_to_record(tab, 'tab', extra))
        
    def test_anytable_to_record_tab_hang(self):
        tab = {'a': [1, 2], 'b': ['a', 'b'], 'c': {'d': 'e'}}
        correct_out = [{'a': 1, 'b': 'a', 'c.d': 'e'}, {'a': 2, 'b': 'b', 'c.d': 'e'}]
        self.assertEqual(correct_out, anytable_to_record(tab, 'tab'))
        
    def test_anytable_to_record_tab_hang_extra(self):
        tab = {'a': [1, 2], 'b': ['a', 'b'], 'c': {'d': 2, 'e': 'a'}}
        extra = {'f': 'g'}
        correct_out = [{'a': 1, 'b': 'a', 'c.d': 2, 'c.e': 'a', 'f': 'g'}, {'a': 2, 'b': 'b', 'c.d': 2, 'c.e': 'a', 'f': 'g'}]
        self.assertEqual(correct_out, anytable_to_record(tab, 'tab', extra))
        
    def test_anytable_to_record_rec(self):
        rec = [{'a': 1, 'b': 'a', 'c.d': 2}, {'a': 2, 'b': 'b', 'c.d': 3}]
        correct_out = [{'a': 1, 'b': 'a', 'c.d': 2}, {'a': 2, 'b': 'b', 'c.d': 3}]
        self.assertEqual(correct_out, anytable_to_record(rec, 'rec'))
        
    def test_anytable_to_record_rec_extra(self):
        rec = [{'a': 1, 'b': 'a'}, {'a': 2, 'b': 'b'}]
        extra = {'c.d': 2}
        correct_out = [{'c.d': 2, 'a': 1, 'b': 'a'}, {'c.d': 2, 'a': 2, 'b': 'b'}]
        self.assertEqual(correct_out, anytable_to_record(rec, 'rec', extra))
        
    ################
    ## build_tab tests
    ################
    
    def test_build_tab_list_recs(self):
        obj = [
            {
                # this is a rec
                'a': 1,
                'b': 'foo',
                'c': [
                    {'d': 1, 'e': 'a'},
                    {'d': 2, 'e': 'b'}
                ]
            },
            {
                # another rec in the same format
                'a': 2,
                'b': 'bar',
                'c': [
                    {'d': 3, 'e': 'c'},
                    {'d': 4, 'e': 'd'}
                ]
            }
        ]
        correct_out = [
            {'a': 1, 'b': 'foo', 'c.d': 1, 'c.e': 'a'},
            {'a': 1, 'b': 'foo', 'c.d': 2, 'c.e': 'b'},
            {'a': 2, 'b': 'bar', 'c.d': 3, 'c.e': 'c'},
            {'a': 2, 'b': 'bar', 'c.d': 4, 'c.e': 'd'}
        ]
        self.assertEqual(correct_out, build_tab(obj))
        
    def test_build_tab_bad(self):
        self.assertEqual([], build_tab(bad_json))
        
    def test_build_tab_multiple_tab_locs(self):
        obj = {'a': {'a': [1, 2], 'b': ['a', 'b']}, 'b': {'a': [3, 4], 'b': ['a', 'b']}}
        with self.assertRaisesRegex(ValueError, "multiple"):
            build_tab(obj)
            
    def test_build_tab_tab(self):
        bball = [
            {
                'name': 'foo',
                'players': [
                    {'name': 'alice', 'hits': [1, 2], 'at-bats': [3, 4]},
                    {'name': 'bob', 'hits': [2], 'at-bats': [3]}
                ]
            },
            {
                'name': 'bar',
                'players': [
                    # this also tests how uneven rows are handled
                    {'name': 'carol', 'hits': [1], 'at-bats': [2, 3]}
                ]
            }
        ]
        correct_out = [
            {
                'name': 'foo', 
                'players.name': 'alice',
                'players.hits': 1,
                'players.at-bats': 3
            },
            {
                'name': 'foo',
                'players.name': 'alice',
                'players.hits': 2,
                'players.at-bats': 4
            },
            {
                'name': 'foo',
                'players.name': 'bob',
                'players.hits': 2,
                'players.at-bats': 3
            },
            {
                'name': 'bar',
                'players.name': 'carol',
                'players.hits': 1,
                'players.at-bats': 2
            },
            {
                'name': 'bar',
                'players.name': 'carol',
                'players.hits': '',
                'players.at-bats': 3
            }
        ]
        self.assertEqual(correct_out, build_tab(bball))

    def test_build_tab_deep_tab(self):
        bball = {'leagues': [
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
        correct_out = [
            {
                'leagues.league': 'American',
                'leagues.teams.name': 'foo',
                'leagues.teams.players.name': 'alice',
                'leagues.teams.players.hits': 1,
                'leagues.teams.players.at-bats': 3
            },
            {
                'leagues.league': 'American',
                'leagues.teams.name': 'bar',
                'leagues.teams.players.name': 'carol',
                'leagues.teams.players.hits': 1,
                'leagues.teams.players.at-bats': 2
            },
            {
                'leagues.league': 'National',
                'leagues.teams.name': 'baz',
                'leagues.teams.players.name': 'bob',
                'leagues.teams.players.hits': 2,
                'leagues.teams.players.at-bats': 3
            },
        ]
        self.assertEqual(correct_out, build_tab(bball))
        
    def test_build_tab_alternate_key_seps(self):
        obj = [
            {
                'a': 1,
                'b': 'foo',
                'c': [
                    {'d': 1, 'e': 'a'},
                ]
            },
            {
                'a': 2,
                'b': 'bar',
                'c': [
                    {'d': 3, 'e': 'c'},
                ]
            }
        ]
        for sep in ['_', '/', '\\', '+']:
            with self.subTest(sep=sep):
                correct_out = [
                    {'a': 1, 'b': 'foo', f'c{sep}d': 1, f'c{sep}e': 'a'},
                    {'a': 2, 'b': 'bar', f'c{sep}d': 3, f'c{sep}e': 'c'},
                ]
                self.assertEqual(correct_out, build_tab(obj, sep))
                
    def test_build_tab_deep_alternate_key_sep(self):
        obj = {'stuff': [
            {
                'name': 'blah',
                'substuff': [
                    {
                        'a': 1,
                        'b': 'foo',
                        'c': [
                            {'d': 1, 'e': 'a'},
                        ]
                    },
                    {
                        'a': 2,
                        'b': 'bar',
                        'c': [
                            {'d': 3, 'e': 'c'},
                        ]
                    }
                ]
            },
            {
                'name': 'wuz',
                'substuff': [
                    {
                        'a': 3, 
                        'b': 'baz', 
                        'c': [
                            {'d': 4, 'e': 'f'}
                        ]
                    }
                ]
            }
        ]}
        sep = '_'
        correct_out = [
            {
                'stuff_name': 'blah',
                'stuff_substuff_a': 1,
                'stuff_substuff_b': 'foo',
                'stuff_substuff_c_d': 1,
                'stuff_substuff_c_e': 'a'
            },
            {
                'stuff_name': 'blah',
                'stuff_substuff_a': 2,
                'stuff_substuff_b': 'bar',
                'stuff_substuff_c_d': 3,
                'stuff_substuff_c_e': 'c'
            },
            {
                'stuff_name': 'wuz',
                'stuff_substuff_a': 3,
                'stuff_substuff_b': 'baz',
                'stuff_substuff_c_d': 4,
                'stuff_substuff_c_e': 'f'
            }
        ]
        self.assertEqual(correct_out, build_tab(obj, sep))
                
    def test_build_tab_sqr(self):
        obj = [
            [1, 2, 'a'],
            [2, 3, 'b']
        ]
        correct_out = [
            {'col1': 1, 'col2': 2, 'col3': 'a'},
            {'col1': 2, 'col2': 3, 'col3': 'b'}
        ]
        self.assertEqual(correct_out, build_tab(obj))
        
    def test_build_tab_sqr_deep(self):
        obj = {'a': [
                {
                    'name': 'blah',
                    'rows': [
                        [1, 2, 'a'],
                        [1, 2, 'a']
                    ]
                }
            ]
        }
        correct_out = [
            {
                'a.name': 'blah', 
                'a.rows.col1': 1, 
                'a.rows.col2': 2, 
                'a.rows.col3': 'a'
            },
            {
                'a.name': 'blah', 
                'a.rows.col1': 1, 
                'a.rows.col2': 2, 
                'a.rows.col3': 'a'
            },
        ]
        self.assertEqual(correct_out, build_tab(obj))

if __name__ == '__main__':
    unittest.main(verbosity=2)
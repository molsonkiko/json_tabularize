from genson import SchemaBuilder
from math import inf
# see https://json-schema.org/learn/miscellaneous-examples.html
# see also https://python-jsonschema.readthedocs.io/en/stable/
# can use genson (https://github.com/wolverdude/GenSON) to create JSON schema
# as well

BASE_SCHEMA = {
  # "$id": "https://example.com/arrays.schema.json",
  # # The $id should be any URI I control
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  # The $schema should be the URI for the rules of the latest draft of JSON
  # schema. Currently the latest is 2020-12.
}


SCALAR_TYPES = {'string', 'number', 'boolean', 'integer', 'null'}


def get_schema(obj):
    builder = SchemaBuilder()
    builder.add_object(obj)
    return builder.to_schema()


def is_listy(x):
    '''returns bool(x is an iterable other than str, bytes, bytearray)
EXAMPLES:
__________
>>> {str(x): is_listy(x) for x in [[], (), '', b'', bytearray(b''), {}, set()]}
{'[]': True, '()': True, '': False, "b''": False, "bytearray(b'')": False, '{}': True, 'set()': True}
    '''
    return hasattr(x, '__iter__') and not isinstance(x, (str, bytes, bytearray))


def classify_schema(schema):
    '''Determines whether a JSON schema represents a scalar ('scal'),
    a array of arrays of scalars ('sqr'),
    an array containing only objects with scalar values ('rec'),
    an object with only scalar and array<scalar> values ('tab'),
    an object or array with only scalar values ('row'),
    or something else ('bad').
    '''
    if schema['type'] in SCALAR_TYPES:
        return 'scal'
    elif schema['type'] == 'array':
        # it's tabular if it contains only arrays of scalars
        # or only objects where all values are scalar.
        item_types = schema['items'].get('type')
        if item_types is None:
            # this is becase it's an 'anyOf' type, where it can have some
            # non-scalars and some scalars as values.
            # This is bad, so we don't want those arrays.
            return 'bad'
        scalar_vals = False
        if isinstance(item_types, list):
            if all(x in SCALAR_TYPES for x in item_types):
                # a list of scalars is not a tabular schema, but a 'row'.
                # rows have desirable properties, though, because we can
                # flatten them list into keys of its parent object.
                return 'row'
            # Disallow arrays that contain some scalars and some non-scalars
            return 'bad'
        elif item_types in SCALAR_TYPES:
            return 'row'
        elif item_types == 'array':
            subarr_types = schema['items']['items'].get('type')
            if subarr_types is None:
                # this is an array containing mixed arrays
                return 'bad'
            elif isinstance(subarr_types, list):
                if all(x in SCALAR_TYPES for x in subarr_types):
                    # this is an array of subarrays containing only scalars
                    return 'sqr'
                # this is an array containing mixed arrays
                return 'bad'
            elif subarr_types in SCALAR_TYPES:
                # this is an array of subarrays that all contain the same
                # scalar type (e.g., a numpy array of dtype int)
                return 'sqr'
            # it's an array containing only objects
            return 'bad'
        # it's an array containing only objects
        subdict_types = [prop.get('type') for prop in schema['items']['properties'].values()]
        cls = 'rec'
        for type_ in subdict_types:
            if not (isinstance(type_, list) or type_ in SCALAR_TYPES):
                # it's a dict containing some non-scalar values; toss it.
                return 'bad'
        # an array of objects with only scalar values is 'records' or 'rec'
        return 'rec'
    # it's an object
    # we start by assuming it's a row. But if the object contains any arrays
    # and isn't bad somehow, we conclude that it's a tab.
    cls = 'row'
    for prop in schema['properties'].values():
        type_ = prop.get('type')
        if type_ is None:
            # we won't try to tabularize objects that have a mixture of
            # non-scalar types
            return 'bad'
        elif type_ == 'object':
            # we will tolerate objects hanging off of our object, so long as
            # those objects contain only scalars (i.e., are 'rows').
            # Such objects can essentially be decomposed into more key-value
            # pairs in the parent object.
            subobj_types = [subprop.get('type') for subprop in prop['properties'].values()]
            if not all(isinstance(type_, list) or type_ in SCALAR_TYPES for type_ in subobj_types):
                return 'bad'
            continue
        elif type_ != 'array':
            # it is OK for a table to have some scalar value
            # and some list values.
            # the scalars are just copy-pasted into the row for each
            # value of the lists.
            continue
        # print(str(prop))
        subarr_type = prop['items'].get('type')
        if isinstance(subarr_type, list):
            if not all(x in SCALAR_TYPES for x in subarr_type):
                # an object mapping to arrays with some non scalars is bad
                return 'bad'
        elif subarr_type not in SCALAR_TYPES:
            # objects mapping to arrays containing non-scalars are bad
            return 'bad'
        # it must be an acceptable array, so now presumptive type is tab.
        cls = 'tab'

    return cls


def find_tabs_in_schema(schema):
    def find(schema, path, tab_paths):
        cls = classify_schema(schema)
        if cls in {'scal', 'row'}:
            # scalars and rows can't have tables as children
            return
        if cls in {'sqr', 'tab', 'rec'}:
            tab_paths[path] = cls
            return
        # by process of elimination, it's bad, so maybe it contains tables
        type_ = schema['type']
        if type_ == 'array':
            items_ = schema['items']
            if 'anyOf' in items_:
                for subschema in items_['anyOf']:
                    find(subschema, path + (inf,), tab_paths)
            else:
                find(items_, path + (inf,), tab_paths)
            return
        props = schema['properties']
        for k, v in props.items():
            find(props[k], path + (k,), tab_paths)

    tab_paths = {}
    find(schema, tuple(), tab_paths)
    return tab_paths


def resolve_hang(hanging_row, key_sep = '.'):
    '''hanging_row: a dict where some values are scalars and others are
    dicts with only scalar values.
Returns: a new dict where the off-hanging dict at key k has been merged into
    the original by adding <k><key_sep><key in hanger> = <val in hanger>
    for each key, val in hanger.
EXAMPLES:
__________
>>> resolve_hang({'a': 'b', 'c': {'d': 'e', 'f': 1}})
{'a': 'b', 'c.d': 'e', 'c.f': 1}
>>> resolve_hang({'a': 'b', 'c': {'d': 'e'}}, '/')
{'a': 'b', 'c/d': 'e'}
    '''
    out = {}
    for k, v in hanging_row.items():
        if isinstance(v, dict):
            for subk, subv in v.items():
                new_key = f'{k}{key_sep}{subk}'
                if new_key in out:
                    raise KeyError(f"Attempted to create hanging row with key {new_key}, but {new_key} was already in {hanging_row}")
                out[new_key] = subv
        else:
            out[k] = v

    return out


def format_key(key, super_key, key_sep = '.'):
    return key if not super_key else f'{key_sep.join(super_key)}{key_sep}{key}'


def anytable_to_record(obj, cls, rest_of_row=None, *, out=None, super_key='', key_sep='.'):
    # print(locals())
    if out is None:
        out = []
    keyformat = lambda x: format_key(x, super_key, key_sep)
    if cls == 'rec':
        # these are arrays of flat objects - this is what we're aiming for
        if rest_of_row is None:
            for rec in obj:
                out.append({keyformat(k): v for k, v in rec.items()})
        else:
            for rec in obj:
                row = {k: v for k, v in rest_of_row.items()}
                row.update({keyformat(k): v for k, v in rec.items()})
                out.append(row)

    elif cls == 'tab':
        # a dict mapping some number of keys to scalars and the rest to arrays
        # Some keys may be mapped to hanging all-scalar dicts and not scalars
        obj_items = obj.items
        arr_dict = {k: v for k, v in obj_items() \
                   if is_listy(v) and not isinstance(v, dict)}
        len_arr = max(len(v) for v in arr_dict.values())
        not_arr_dict = resolve_hang({keyformat(k): v for k, v in obj_items() if k not in arr_dict})
        if rest_of_row is None:
            for ii in range(len_arr):
                row = {} if not not_arr_dict else {k: v for k, v in not_arr_dict.items()}
                for k, v in arr_dict.items():
                    # float('nan') and None become strings that Excel
                    # doesn't like
                    # Probably the most reliable cross-application
                    # representation of missing values in a mixed-type
                    # array is ''
                    row[keyformat(k)] = '' if ii >= len(v) else v[ii]
                out.append(row)
        else:
            # there were other keys leading up to the table
            for ii in range(len_arr):
                row = {} if not not_arr_dict else {k: v for k, v in not_arr_dict.items()}
                row.update({k: v for k, v in rest_of_row.items()})
                for k, v in arr_dict.items():
                    row[keyformat(k)] = '' if ii >= len(v) else v[ii]
                out.append(row)

    elif cls == 'sqr':
        for arr in obj:
            row = {} if rest_of_row is None else {k: v for k, v in rest_of_row.items()}
            for ii, v in enumerate(arr):
                row[keyformat(f'col{ii+1}')] = v
            out.append(row)

    return out


def build_tab(obj, key_sep='.'):
    '''Find anything in the JSON object obj that could be converted into a
    table, and export a list of dicts, suitable for conversion into a pandas
    DataFrame, writing to a file with csv.DictWriter,
    or any number of other applications.
Since this recursively searches the JSON, key_sep is used to separate parent
from child keys in the column names of the output.
    '''
    def build(obj, cls, depth, tab_path, out, cur_row = None, cur_key = None, key_sep='.'):
        # print(locals())
        if cur_key is None:
            cur_key = []
        if depth == len(tab_path):
            anytable_to_record(obj, cls, cur_row, out=out, super_key=cur_key, key_sep=key_sep)
            return
        else:
            if isinstance(obj, list):
                for subobj in obj:
                    if cur_row is None:
                        cur_row = {}
                    build(subobj, cls, depth+1, tab_path, out, cur_row, cur_key, key_sep)
            else:
                new_key = tab_path[depth]
                if cur_row is None:
                    cur_row = {}
                for k, v in obj.items():
                    if k != new_key:
                        k = format_key(k, cur_key, key_sep)
                        if isinstance(v, dict):
                            for subk, subv in v.items():
                                if not is_listy(subv):
                                    cur_row[f'{k}{key_sep}{subk}'] = subv
                        elif not is_listy(v):
                            cur_row[k] = v
                build(obj[new_key], cls, depth+1, tab_path, out, cur_row, cur_key + [new_key], key_sep)

    schema = get_schema(obj)
    tab_paths = find_tabs_in_schema(schema)
    if not tab_paths:
        return []
    if len(tab_paths) > 1:
        raise ValueError("This JSON contains multiple possible tables, so build tabs doesn't know how to proceed.")
    out = []
    path, cls = list(tab_paths.items())[0]
    build(obj, cls, 0, path, out, key_sep=key_sep)
    
    return out
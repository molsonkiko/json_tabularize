'''
An unusually powerful algorithm for converting JSON into a tabular format, which is defined as an array of flat (all scalar values) objects.

Every algorithm I've seen for making JSON into a table can't fully normalize very deeply nested JSON, but instead produces partially normalized JSON where some rows in the resultant table just have raw un-normalized JSON.
'''
__version__ = '1.0.3'

from json_tabularize.tabularize import SchemaBuilder, get_schema, build_tab

__all__ = ['SchemaBuilder', 'get_schema', 'build_tab', 'test']
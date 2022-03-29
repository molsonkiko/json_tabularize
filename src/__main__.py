from json_tabularize.tabularize import *
import json
import os
import sys

if __name__ == '__main__':
	fname = ' '.join(sys.argv[1:])
	with open(fname) as f:
		js = json.load(f)
	
	tab = build_tab(js)
	print(json.dumps(tab, indent=4))
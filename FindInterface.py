#!/usr/bin/env python                                                           

import os,sys
import pdb

chromium_path = os.path.abspath(
    os.path.join(os.environ['HOME'], 'chromium', 'src'))
blink_bindings_path = os.path.join(
    chromium_path, 'third_party', 'WebKit', 'Source', 'bindings', 'scripts')
sys.path.insert(0, blink_bindings_path)

from blink_idl_parser import parse_file, BlinkIDLParser


def find_all_files(directory):
    for root, dirs, files in os.walk(directory):
        yield root
        for file in files:
            yield os.path.join(root, file)

def find_idl_files(dir_name):
    idl_file_list = []
    for file in find_all_files(dir_name):
	#import pdb
	#pdb.set_trace()
        if file.endswith('.idl') and not os.path.basename(file) == 'InspectorInstrumentation.idl':
            idl_file_list.append(file)
    return idl_file_list


def find_interface(node,idl_fname,depth=0):
    interface_name_list = []
    idlfname_and_interface = {}
    return_list = []
    count_interface = 0
    for child in node.GetChildren():
        if child.GetClass().startswith('Interface'):
            interface_name_list.append(child.GetName())
	    count_interface += 1
            #if found_interface > 0:
		#idlfname_and_interface[idl_fname] = interface_name_list
    if count_interface > 0:
	interface_name_list.insert(0,count_interface)
	idlfname_and_interface[idl_fname] = interface_name_list
    return idlfname_and_interface
	


def main(dir_name):
    list_of_interface = []
    for idl_file in find_idl_files(dir_name):
        #import pdb
        #pdb.set_trace()
        parser = BlinkIDLParser(debug=False)
        definitions = parse_file(parser, idl_file)
        idlfname_and_interface = find_interface(definitions,os.path.basename(idl_file))
        if not idlfname_and_interface == {}:
	    list_of_interface.append(idlfname_and_interface)
    return list_of_interface
    

if __name__ == '__main__':
    flag = 0
    list_of_interface = main(sys.argv[1]) 
    print list_of_interface
    print 'the number of files is ', len(list_of_interface)
    for interface in list_of_interface:
        for val in interface.values():
	    if not val[0] == 1:
		flag += 1
                print 'not one time!'
	        break
	if flag > 0:
		break
    if flag == 0:
	print 'all interface names appear only on time :)'

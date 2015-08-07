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
        if file.endswith('.idl') and not os.path.basename(file) == 'InspectorInstrumentation.idl':
            idl_file_list.append(file)
    return idl_file_list



def find_interface(node,idl_fname,depth=0):
    #a list includes interface names and the number of them
    interface_name_list = []

    #a dictionary includes idl files and a list of interface names  
    idlfname_and_interface = {}

    #a list includes idlfname_and_interface and interface_name_list
    return_list = []

    #in this for statment, we can get interface_name_list in one idl file
    for child in node.GetChildren():
        if child.GetClass().startswith('Interface'):
            interface_name_list.append(child.GetName())

    #a value indicates the number of interfaces
    count_interface = len(interface_name_list)

    #if the number of interface is more than one,append the interface_name_list to the idlfname_and_interface.
    #(if there are not some interfaces in a idl file, this program doesn't append the empty interface_name_list. )
    if count_interface:
	interface_name_list.insert(0,count_interface)
	idlfname_and_interface[idl_fname] = interface_name_list
    return idlfname_and_interface
	


def main(dir_name):
    #a list includes idl file names and interface name list. 
    list_of_interface = []

    #a for statement to find interface names in one idl file.
    for idl_file in find_idl_files(dir_name):
        parser = BlinkIDLParser(debug=False)
        definitions = parse_file(parser, idl_file)
        idlfname_and_interface = find_interface(definitions,os.path.basename(idl_file))
        
        #if there is a empty dictionary, this program doesn't append it to list_of_interface
        #because find_interface() returns some empty dictionary when there are not some interfaces in a idl file 
        if not idlfname_and_interface == {}:
	    list_of_interface.append(idlfname_and_interface)
    return list_of_interface
    

if __name__ == '__main__':
    list_of_interface = main(sys.argv[1]) 
    print list_of_interface
    print 'the number of files is ', len(list_of_interface)
    
    #in find_interface function, the number of interfaces is resistered.
    #this for statement checks whether the number is one or not.
    #if the number is more than one,this program  returns 'not one time!'
    for interface in list_of_interface:
        for val in interface.values():
	    if not val[0] == 1:
                print 'not one time!'
		sys.exit()
    print 'all interface names appear only on time :)'

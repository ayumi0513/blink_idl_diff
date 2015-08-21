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

    #a list includes idl files and a list of interface names  
    idlfname_interface = {} 

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
	idlfname_interface[idl_fname] = interface_name_list
    return idlfname_interface
	



#this is a function to make a dictionary whose key is idl file name and value is interface names
#this function runs first in this program
def make_idlfname_interface_dict(node_and_idlfname_list):
    #a dictionary includes idl file names and interface name list.
    all_idlfname_interface = {}
   
    #find interface names in one idl file.
    for node,idl_fname in node_and_idlfname_list:
        idlfname_interface = find_interface(node,idl_fname)
        #if there is a empty dictionary, this program doesn't append it to list_of_interface
        #because find_interface() returns some empty dictionary when there are not some interfaces in a idl file
        if not idlfname_interface == {}:
            for idlfname, interface in idlfname_interface.items():
                all_idlfname_interface[idlfname] = interface
    return all_idlfname_interface


#this is a function to make a dictionary whose key is interface name and value is idl file names
def make_interface_idlfname_dict(all_idlfname_interface):
    all_interface_idlfname = {}
    for idlfname,interface in all_idlfname_interface.items():
        if interface[1] in all_interface_idlfname:
            all_interface_idlfname[interface[1]].append(idlfname)
        else:
            all_interface_idlfname[interface[1]] = [idlfname]
    return all_interface_idlfname


#get_interface_node func and get_content_of_interface func are used to know the content of Interface
def get_interface_node(node):
    interface_node_list = []
    for child in node.GetChildren():
        if child.GetClass().startswith('Interface'):
            interface_node_list.append(child)
    if not interface_node_list == []:
        return interface_node_list


#def get_content_of_interface(interface_node_list):
    #interface_content_list = []
    #for interface_node in interface_node_list:
        #for child in interface_node.GetChildlen():
            #interface_content_list.append(child.GetName())
    #print interface_content_list
        

def main(dir_name):
    node_and_idlfname = []
    def_basename = {}
    for idl_file in find_idl_files(dir_name):
        parser = BlinkIDLParser(debug=False)
        definitions = parse_file(parser, idl_file)
        node_and_idlfname.append([definitions,os.path.basename(idl_file)])
    return node_and_idlfname 
       

#this function checks whether the number of interface name in one idl fileis is one or not.
#if the number is more than one,this function  returns False
#if the number is one, this function returns True
def count_interfacename(interfacenames):
    for interfacename in interfacenames:
	if not interfacename[0] == 1:
	    return False
    return True 


if __name__ == '__main__':
    idlfname_interface = make_idlfname_interface_dict(main(sys.argv[1]))
    #print idlfname_interface
    
    #in find_interface function, the number of interface names is resistered, so check the number here.
    if count_interfacename(idlfname_interface.values()):
        print 'all interface names appear only one time :)'
    else:
	print 'not noe time :('

    interface_idlfname = make_interface_idlfname_dict(idlfname_interface)
    #print interface_idlfname
    #for idlfiles_list in interface_idlfname.values():
	#if len(idlfiles_list) > 1:
	    #print idlfiles_list
    for node,idl_fname in main(sys.argv[1]):
        get_content_of_interface(get_interface_node(node))
    print 'the number of idl files is ', len(idlfname_interface)
    print 'the number of interface name is', len(interface_idlfname)

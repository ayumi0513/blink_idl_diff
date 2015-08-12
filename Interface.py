#!/usr/bin/env python                                                           

import os,sys
import pdb


chromium_path = os.path.abspath(
    os.path.join(os.environ['HOME'], 'chromium', 'src'))
blink_bindings_path = os.path.join(
    chromium_path, 'third_party', 'WebKit', 'Source', 'bindings', 'scripts')
sys.path.insert(0, blink_bindings_path)

from blink_idl_parser import parse_file, BlinkIDLParser


extension_name = '.idl'
non_blink_idl_files = ['InspectorInstrumentation.idl']

def find_all_files(directory):
    for root, dirs, files in os.walk(directory):
        yield root
        for file in files:
            yield os.path.join(root, file)

def find_idl_files(dir_name):
    idl_file_list = []
    for file in find_all_files(dir_name):
        if file.endswith('.idl') and os.path.basename(file) not in non_blink_idl_files:
            idl_file_list.append(file)
    return idl_file_list


#make a list includes touples have definition(node) and idl file name
def make_node_idlfname_list(dir_name):
    node_and_idlfname = []
    parser = BlinkIDLParser(debug=False)
    for idl_file in find_idl_files(dir_name):
        definitions = parse_file(parser, idl_file)
        node_and_idlfname.append((definitions,os.path.basename(idl_file)))
    return node_and_idlfname



def find_interface(node_and_idlfname):
    idlfname_interface = {}
    for node, idlfname in node_and_idlfname:
        interface_name_list = []
        for child in node.GetChildren():
            if child.GetClass().startswith('Interface'):
                #'if not' means we return interface names include partial interface name
                if not is_partial(child):
                    interface_name_list.append(child.GetName())
        if len(interface_name_list):
            idlfname_interface[idlfname] = interface_name_list
    return idlfname_interface



def is_partial(node):
    #if the node is partial, return True
    return node.GetProperty('Partial', default = False)

    

#this func must use after we get idlfname_interface dict from find_interface func
def find_idlfname(idlfname_interface):
    interface_idlfname = {}
    for idlfname, interface_list in idlfname_interface.items():
        for interface in interface_list:
            if interface in interface_idlfname:
                interface_idlfname[interface].append(idlfname)
            else:
                interface_idlfname[interface] = [idlfname] 	
    return interface_idlfname


def find_attribute(node_and_idlfname):
    for node, idlfname in node_and_idlfname:
        for interface in  node.GetListOf('Attribute'):
            print interface.GetName()


def main(dir_name):
    node_and_idlfname_list = make_node_idlfname_list(dir_name)
    idlfname_interface_dict = find_interface(node_and_idlfname_list)
    #print idlfname_interface_dict
    print 'the number of idl files is', len(idlfname_interface_dict)
    for interface_list in idlfname_interface_dict.values():
        if not len(interface_list) == 1:
            print 'Some idl files include more than interface name'
            sys.exit()
    print 'All idl files include ONLY ONE interface name'
    #print find_idlfname(idlfname_interface_dict)
    print find_attribute(node_and_idlfname_list)

   
if __name__ == '__main__':
    main(sys.argv[1])

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



def find_interfaces(node_and_idlfname):
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
def find_idlfnames(idlfname_interface):
    interface_idlfname = {}
    for idlfname, interface_list in idlfname_interface.items():
        for interface in interface_list:
            if interface in interface_idlfname:
                interface_idlfname[interface].append(idlfname)
            else:
                interface_idlfname[interface] = [idlfname] 	
    return interface_idlfname


#it is just getting a interfaces list
def get_interfaces(node_and_idlfname):
    interfaces = []
    for node, idlfname in node_and_idlfname:
        for interface in node.GetListOf('Interface'):
            interfaces.append(interface.GetName())
    return interfaces




#it is just getting a attributes list
def get_attributes(node_and_idlfname):
    attributes = []
    for node, idlfname in node_and_idlfname:
        for interface in node.GetListOf('Interface'):
            for child in node.GetChildren():
                for attribute in  child.GetListOf('Attribute'):
                        attributes.append(attribute.GetName())
    return attributes


def get_attributes2(interface):
    attributes = []
    for child in interface.GetChildren():
        if child.GetClass() == 'Attribute':
            attributes.append(child)
    return attributes

            
def get_attributes(interface):
    return interface.GetListOf('Attribute')


def get_type(attribute):
    return attribute.GetChildren()[0].GetChildren()[0].GetName() 


def output_elements(node_and_idlfname):
    attributes = []
    for node, idlfname in node_and_idlfname:
        for child in node.GetChildren():
            if child.GetClass() == 'Interface':
                print child.GetName()
                for attribute in get_attributes(child):
                    print '  a:', attribute.GetName(), '    t:', get_type(attribute)

def get_node_of_interface(node_and_idlfname):
    node_of_interface = []
    for node,idlfname in node_and_idlfname:
        for interface in node.GetListOf('Interface'):
            node_of_interface.append(interface)
    return node_of_interface



def get_node_of_attribute(node_of_interface):
    for node in node_of_interface:
        #print node.GetName()
        for child in node.GetChildren():
            for attribute in  child.GetListOf('Attribute'):
                print '  ', attribute.GetName()


def main(argv):
    dir_name = argv[0]
    node_and_idlfname_list = make_node_idlfname_list(dir_name)
    idlfname_interface_dict = find_interfaces(node_and_idlfname_list)
    #print idlfname_interface_dict
    print 'the number of idl files is', len(idlfname_interface_dict)
    for interface_list in idlfname_interface_dict.values():
        if not len(interface_list) == 1:
            print 'Some idl files include more than interface name'
            sys.exit()
    print 'All idl files include ONLY ONE interface name'
    #print find_idlfnames(idlfname_interface_dict)
    #print get_interfaces(node_and_idlfname_list)
    #print get_attributes(node_and_idlfname_list)
    output_elements(node_and_idlfname_list)    
    #node_of_interface = get_node_of_interface(node_and_idlfname_list)
    #get_node_of_attribute(node_of_interface)

if __name__ == '__main__':
    main(sys.argv[1:])

#!/usr/bin/env python

import os,sys
import pdb
import json

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



def make_node_list(dir_name):
    node_list = []
    parser = BlinkIDLParser(debug=False)
    for idl_file in find_idl_files(dir_name):
        definitions = parse_file(parser, idl_file)
        node_list.append(definitions)
    return node_list

def get_idlfname(node):
    return os.path.basename(node.GetProperty('FILENAME'))


def make_idlfname_interface_dict(node_list):
    idlfname_interface = {}
    for node in node_list:
        interface_name_list = []
        for child in node.GetChildren():
            if child.GetClass().startswith('Interface'):
                #'if not' means we return only non_ partial interface names
                if is_partial(child):
                    pass
                else:
                    interface_name_list.append(child.GetName())
        if len(interface_name_list):
            idlfname_interface[get_idlfname(node)] = interface_name_list
    return idlfname_interface



def is_partial(node):
    #if the node is partial, return True
    return node.GetProperty('Partial', default = False)

designated_idlfname = 'Storage.idl'

def get_properties(node_list):
    print '~~~~~~~~GetProperties~~~~~~~~~'
    for node in node_list:
        if get_idlfname(node) == 'Storage.idl':
            properties =  node.GetProperties()
    return properties

#this func must use after we get idlfname_interface dict from make_idlfname_interface_dict func
def make_interface_idlfname_dict(idlfname_interface):
    interface_idlfname = {}
    for idlfname, interface_list in idlfname_interface.items():
        for interface in interface_list:
            if interface in interface_idlfname:
                interface_idlfname[interface].append(idlfname)
            else:
                interface_idlfname[interface] = [idlfname]
    return interface_idlfname



def get_interfaces(node):
    return node.GetListOf('Interface')

def get_attributes(interface_node):
    return interface_node.GetListOf('Attribute')

def get_operations(interface_node):
    return interface_node.GetListOf('Operation')


def get_type(node):
    type_node = node.GetListOf('Type')[0]
    return type_node.GetChildren()[0]

    return interface_node.GetListOf('Operation')

def get_arguments(operation_node):
    arguments = []
    arguments_node = operation_node.GetListOf('Arguments')[0]
    for argument_node in arguments_node.GetListOf('Argument'):
        arguments.append(argument_node)
    return arguments


def make_idlfname_json(idlfname_interface_dict):
    return json.dumps(idlfname_interface_dict, indent = 4)

def get_operation_names(operation_node_list):
    operation_name_list = []
    for operation_node in operation_node_list:
        operation_name_list.append(operation_node.GetName())
    return operation_name_list

def make_json_file(node_list):
    json_data = {}
    for node in node_list:
        json_value = {}
        for interface_node in get_interfaces(node):
            interface_value = []
            for operation_node in get_operations(interface_node):
                ope_arg_list = []
                opetype_opename = (get_type(operation_node).GetName(),operation_node.GetName())
                ope_arg_list.append(opetype_opename)
                for argument_node in get_arguments(operation_node):
                    argtype_argname = (get_type(argument_node).GetName(),argument_node.GetName())
                    ope_arg_list.append(argtype_argname)
                interface_value.append(ope_arg_list)
            for attribute_node in get_attributes(interface_node):
                attritype_attriname = (get_type(attribute_node).GetName(), attribute_node.GetName())
                interface_value.append(attritype_attriname)
            json_value[interface_node.GetName()] = interface_value
        json_data.setdefault(get_idlfname(interface_node),[]).append(json_value)
    with  open('json_file.json','w') as f:
        json.dump(json_data,f,sort_keys=True,indent=4)
        f.close()


def main(argv):
    dir_name = argv[0]
    node_list = make_node_list(dir_name)
    idlfname_interface_dict = make_idlfname_interface_dict(node_list)
    #print idlfname_interface_dict
    #print make_idlfname_json(idlfname_interface_dict)
    #print make_json(node_list)
    print 'the number of idl files is', len(idlfname_interface_dict)
    for interface_list in idlfname_interface_dict.values():
        if not len(interface_list) == 1:
            print 'Some idl files include more than interface name'
            sys.exit()
    print 'All idl files include ONLY ONE interface name'
    #print find_idlfnames(idlfname_interface_dict)
    #output_interfaces_attributes_types(node_list)
    #output_interfaces_operations(node_list)
    #print get_properties(node_list)
    make_json_file(node_list)

if __name__ == '__main__':
    main(sys.argv[1:])

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



def number_of_interfaces(idlfname_interface_dict):
    for interface_list in idlfname_interface_dict.values():
        if not len(interface_list) == 1:
            return 'Some idl files include more than interface name'
            sys.exit()
    return 'All idl files include ONLY ONE interface name'


def get_idl_properties(node_list):
    print '~~~~~~~~GetIdlProperties~~~~~~~~~'
    for node in node_list:
        if get_idlfname(node) == 'Storage.idl':
            properties =  node.GetProperties()
    return properties


designated_idlfname = 'Storage.idl'

def get_operation_properties(node_list):
    print '~~~~~~~~GetOperationProperties~~~~~~~~~'
    properties = []
    for node in node_list:
        if get_idlfname(node) == designated_idlfname:
            for interface in get_interfaces(node):
                for operation in get_operations(interface):
                    properties.append(operation.GetProperties())
    return properties



def get_interfaces(node):
    return node.GetListOf('Interface')


def get_attributes(interface_node):
    return interface_node.GetListOf('Attribute')


def get_consts(interface_node):
    return interface_node.GetListOf('Const')

#return type and value list of const
def get_const_type_value(interface_node):
    return interface_node.GetChildren()


def get_operations(interface_node):
    return interface_node.GetListOf('Operation')


def get_type(node):
    type_node = node.GetListOf('Type')[0]
    return type_node.GetChildren()[0]


def get_arguments(operation_node):
    arguments = []
    arguments_node = operation_node.GetListOf('Arguments')[0]
    for argument_node in arguments_node.GetListOf('Argument'):
        arguments.append(argument_node)
    return arguments


def get_argument_value(argument_node):
    argument_value = {}
    argument_value['Type'] = get_type(argument_node).GetName()
    argument_value['Name'] = argument_node.GetName()
    return argument_value


def get_operation_value(operation_node,argument_list):
    operation_value = {}
    operation_value['Type'] = get_type(operation_node).GetName()
    if operation_node.GetProperty('GETTER',default=None):
        operation_value['Name']  = '__getter__'
    elif operation_node.GetProperty('SETTER',default=None):
        operation_value['Name'] = '__setter__'
    elif operation_node.GetProperty('DELETER',default=None) :
        operation_value['Name']  = '__deleter__'
    else:
        operation_value['Name'] = operation_node.GetName()
    operation_value['Argument'] = argument_list
    return operation_value

def get_attribute_value(attribute_node):
    attribute_value = {}
    attribute_value['Type'] = get_type(attribute_node).GetName()
    attribute_value['Name'] = attribute_node.GetName()
    return attribute_value

def get_const_value(const_node):
    const_value = {}
    const_value['Type'] = get_const_type_value(const_node)[0].GetName()
    const_value['Name'] = const_node.GetName()
    const_value['Value'] = get_const_type_value(const_node)[1].GetName()
    return const_value

def get_interface_value(interface_node,operation_list,attribute_list,const_list):
    interface_value = {}
    interface_value['Name'] = interface_node.GetName()
    interface_value['Operation'] = operation_list
    interface_value['Attribute'] = attribute_list
    interface_value['Const'] = const_list
    interface_value['FileName'] = get_idlfname(interface_node)
    return interface_value

def get_idl_value(interface_list):
    idl_value = {}
    idl_value['Interface'] = interface_list
    return idl_value

def make_json_file(node_list):
    json_data = []
    for node in node_list:
        for interface_node in get_interfaces(node):
            operation_list, attribute_list, const_list = [], [], []
            for operation_node in get_operations(interface_node):
                argument_list = []
                for argument_node in get_arguments(operation_node):
                     argument_list.append(get_argument_value(argument_node))
                operation_list.append(get_operation_value(operation_node,argument_list))
            for attribute_node in get_attributes(interface_node):
                attribute_list.append(get_attribute_value(attribute_node))
            for const_node in get_consts(interface_node):
                const_list.append(get_const_value(const_node))
            json_data.append(get_interface_value(interface_node,operation_list,attribute_list,const_list))
    with  open('json_file.json','w') as f:
        json.dump(json_data,f,indent=4)
        f.close()


def main(argv):
    dir_name = argv[0]
    node_list = make_node_list(dir_name)
    idlfname_interface_dict = make_idlfname_interface_dict(node_list)
    print 'the number of idl files is', len(idlfname_interface_dict)
    print number_of_interfaces(idlfname_interface_dict)
    make_json_file(node_list)
    #print get_operation_properties(node_list)

if __name__ == '__main__':
    main(sys.argv[1:])

import json
import sys

json_fname1 = 'shortA.json'
json_fname2 = 'shortB.json'

def get_json_data(fname):
    f = open(fname,'r')
    json_data = json.load(f)
    #print json.dumps(json_data,sort_keys=True,indent=4)
    f.close()
    return json_data


def get_idl_and_interface_name(json_data):
    return [json_data['FileName'],json_data['Name']]


def get_attributes(json_data):
    return json_data['Attribute']


def get_operations(json_data):
    return json_data['Operation']


def get_consts(json_data):
    return json_data['Const']


def added_attribute(json_data1,json_data2):
    output = []
    idl_and_interface = get_idl_and_interface_name(json_data1)
    #idl_and_interface = get_idl_and_interface_name(json_data2)
    attributes1 = get_attributes(json_data1)
    attributes2 = get_attributes(json_data2)
    for attr1 in attributes1:
        if not attr1 in attributes2:
            output.append('attribute(Type:{0},Name:{1}) is added to {2}(Interface:{3})'.format(attr1['Type'],attr1['Name'],idl_and_interface[0],idl_and_interface[1]))
    return output


def deleted_attribute(json_data1,json_data2):
    output = []
    idl_and_interface = get_idl_and_interface_name(json_data1)
    #idl_and_interface = get_idl_and_interface_name(json_data2)
    attributes1 = get_attributes(json_data1)             
    attributes2 = get_attributes(json_data2)
    for attr2 in attributes2:
        if not attr2 in attributes1:
            output.append('attribute(Type:{0},Name:{1}) is deleted from {2}(Interface:{3})'.format(attr2['Type'],attr2['Name'],idl_and_interface[0],idl_and_interface[1]))
    return output


def added_opertaion(json_data1,json_data2):
    output = []
    idl_and_interface = get_idl_and_interface_name(json_data1)
    #idl_and_interface = get_idl_and_interface_name(json_data2)
    operations1 = get_operations(json_data1)             
    operations2 = get_operations(json_data2)
    for ope1 in operations1:                             
        if not ope1 in operations2:                                         
            output.append('operation(Type:{0},Name:{1}) is added to {2}(Interface:{3})'.format(ope1['Type'],ope1['Name'],idl_and_interface[0],idl_and_interface[1]))
    return output


def deleted_operation(json_data1,json_data2):
    output = []
    idl_and_interface = get_idl_and_interface_name(json_data1)
    #idl_and_interface = get_idl_and_interface_name(json_data2)
    operations1 = get_operations(json_data1)             
    operations2 = get_attributes(json_data2)
    for ope2 in operations2:
        if not ope2 in operations1:                        
            output.append('operation(Type:{0},Name:{1}) is deleted from {2}(Interface:{3})'.format(ope2['Type'],ope2['Name'],idl_and_interface[0],idl_and_interface[1]))
    return output


def added_const(json_data1,json_data2):
    output = []        
    idl_and_interface = get_idl_and_interface_name(json_data1)
    #idl_and_interface = get_idl_and_interface_name(json_data2)
    consts1 = get_consts(json_data1)             
    consts2 = get_consts(json_data2)
    for cons1 in consts1:                             
        if not cons1 in consts2:                                         
            output.append('const(Type:{0},Name:{1}) is added to {2}(Interface:{3})'.format(cons1['Type'],cons1['Name'],idl_and_interface[0],idl_and_interface[1]))
    return output


def deleted_const(json_data1,json_data2):
    output = [] 
    idl_and_interface = get_idl_and_interface_name(json_data1)
    #idl_and_interface = get_idl_and_interface_name(json_data2)
    consts1 = get_consts(json_data1)             
    consts2 = get_consts(json_data2)
    for cons2 in consts2:
        if not cons2 in consts1:                        
            output.append('const(Type:{0},Name:{1}) is deleted from {2}(Interface:{3})'.format(cons2['Type'],cons2['Name'],idl_and_interface[0],idl_and_interface[1]))
    return output



def all_added_diff(json_data1,json_data2):
    output = []
    if added_attribute(json_data1,json_data2):
        for added_attr in added_attribute(json_data1,json_data2):
            output.append(added_attr)
    if added_opertaion(json_data1,json_data2):
        for added_ope in added_opertaion(json_data1,json_data2):
            output.append(added_ope)
    if added_const(json_data1,json_data2):
        for added_cons in added_const(json_data1,json_data2):
            output.append(added_cons)

    return output

def all_deleted_diff(json_data1,json_data2):
    output = []
    if deleted_attribute(json_data1,json_data2):
        for deleted_attr in deleted_attribute(json_data1,json_data2):
            output.append(deleted_attr)
    if deleted_operation(json_data1,json_data2):
        for deleted_ope in deleted_operation(json_data1,json_data2):
            output.append(deleted_ope)
    if deleted_const(json_data1,json_data2):
        for deleted_cons in deleted_const(json_data1,json_data2):
            output.append(deleted_cons)
    return output


def print_all_diff(json_data1,json_data2):
    print ' '
    print '[Added]'
    for e in all_added_diff(json_data1,json_data2):
        print e
    print ' '    
    print '[Deleted]'
    for e in all_deleted_diff(json_data1,json_data2):
        print e



def main(argv):
    json_data1 = get_json_data(json_fname1)
    json_data2 = get_json_data(json_fname2)
    print_all_diff(json_data1,json_data2)

if __name__ == '__main__':
    main(sys.argv[1:])

import json
import sys
from collections import OrderedDict


def load_json_data(filepath):
    """load a json file into a dictionary
    Arg : A file path of a json file that we want to load
    Return:
        a dictionary that is loaded from the json file
    """
    with open(filepath,'r') as f:
        return json.load(f)


def sort_member(interface_content):
    """Sort the order of members like below.
       [ExtAttributes->Const->Attribute->Operation]
        Arg : The content of an interface
        Return : The sorted content of an interface
    """
    sorted_interface_content = OrderedDict()
    extattributes = []
    const = []
    attribute = []
    operation = []
    for member_name, member_content in interface_content.items():
        if member_name == 'ExtAttributes':
            extattributes = member_content
        elif member_name == 'Const':
            const = member_content
        elif member_name == 'Attribute':
            attribute = member_content
        elif member_name == 'Operation':
            operation = member_content
    sorted_interface_content['ExtAttributes'] = extattributes
    sorted_interface_content['Const'] = const
    sorted_interface_content['Attribute'] = attribute
    sorted_interface_content['Operation'] = operation
    if 'diff_tag' in interface_content.keys():
        sorted_interface_content['diff_tag'] = interface_content['diff_tag']
    return sorted_interface_content


def sort_diff_data_by_tags(diff_data):
    """Sort diff_data using diff_tag.
        Arg : A dictionary that is loaded by load_json_data().
        Return : A sorted dictionary
    """
    sorted_diff = OrderedDict()
    interface_name_deleted_whole = []
    interface_name_added_whole = []
    interface_name_changed_part = []
    changed_interface_content = OrderedDict()
    for interface_name, interface_content in diff_data.items():
        if 'diff_tag' in interface_content.keys():
            if interface_content['diff_tag'] == 'deleted':
                interface_name_deleted_whole.append(interface_name)
            else:
                interface_name_added_whole.append(interface_name)
        else:
            interface_name_changed_part.append(interface_name)
    for interface_name in sorted(interface_name_changed_part):
        gathered_member_content = OrderedDict()
        for member_name, member_contents in diff_data[interface_name].items():
            gather_member_content = []
            deleted_content = []
            added_content = []
            unchanged = []
            for member_content in member_contents:
                if 'diff_tag' in member_content.keys():
                    if member_content['diff_tag'] == 'deleted':
                        deleted_content.append(member_content)
                    else:
                        added_content.append(member_content)
                else:
                    unchanged.append(member_content)
            for content in deleted_content:
                gather_member_content.append(content)
            for content in added_content:
                gather_member_content.append(content)
            for content in unchanged:
                gather_member_content.append(content)
            gathered_member_content[member_name] = gather_member_content
        changed_interface_content[interface_name] = gathered_member_content
    for interface_name in sorted(interface_name_deleted_whole):
        sorted_diff[interface_name] = sort_member(diff_data[interface_name])
    for interface_name in sorted(interface_name_added_whole):
        sorted_diff[interface_name] = sort_member(diff_data[interface_name])
    for interface_name, interface_content in changed_interface_content.items():
        sorted_diff[interface_name] = sort_member(interface_content)
    return sorted_diff


def replace_diff_tag(diff_tag):
    """If diff_tag is 'deleted', replace 'deleted' for '-'. 
       If diff_tag is 'added', replace 'added' for '+'.
       Arg : 'deleted' or 'added'
       Return : '-' or '+'
    """
    if diff_tag == 'deleted':
        diff_tag = '-'
    else:
        diff_tag = '+'
    return diff_tag


def whether_diff_tag_exist(content):
    """judge whether diff_tag is exist or not.
        Arg : A dictionary that possibly has diff_tag.
        Return : If input has 'diff_tag' in that of keys, return that of value. Otherwise return nothing.
    """
    if 'diff_tag' in content.keys():
        diff_tag = replace_diff_tag(content['diff_tag'])
    return diff_tag



def print_extattribute(extattributes):
    """Print a content of extattribute.
        Arg : A list consists of a content of an extattribute
    """
    for extattributes_content in extattributes:
        if 'diff_tag' in extattributes_content.keys():
            diff_tag = replace_diff_tag(extattributes_content['diff_tag'])
            print '    {TAG}'.format(TAG=diff_tag),
        else:
            print '    *',
        print '{NAME}'.format(NAME=extattributes_content['Name'])


def print_const(const):
    """Print a content of const.
        Arg : A list consists of a content of a const
    """
    for const_content in const:
        if 'diff_tag' in const_content.keys():
            diff_tag = replace_diff_tag(const_content['diff_tag'])
            print '    {TAG}'.format(TAG=diff_tag),
        else:
            print '    *',
        print '{TYPE}'.format(TYPE=const_content['Type']),
        print '{NAME}'.format(NAME=const_content['Name']),
        print '={VALUE}'.format(VALUE=const_content['Value'])


def print_extattributes_of_attribute_and_operation(extattributes):
    """Print extattributes in attribute or operation.
        Arg : A dictionary whose key is 'ExtAttributes' and value is a list of extattributes
    """
    sys.stdout.write('[')
    count = 0
    for extattributes_content in extattributes:
        count += 1
        sys.stdout.write(extattributes_content['Name']) 
        if count < len(extattributes):
            print ', ',
    print ']',


def print_attribute(attribute):
    """Print a content of attribute.
        Arg : A list consists of a content of an attribute
    """
    for attribute_content in attribute:
        if 'diff_tag' in attribute_content.keys():
            diff_tag = replace_diff_tag(attribute_content['diff_tag'])
            print '    {TAG}'.format(TAG=diff_tag),
        else:
            print '    *',
        if attribute_content['ExtAttributes']:
            print_extattributes_of_attribute_and_operation(attribute_content['ExtAttributes'])
        print attribute_content['Type'],
        print attribute_content['Name']


def print_argument(argument):
    """Print an argument in an operation.
        Arg : A dictionary whose key is 'Argument' and value is a list of argument
    """
    count = 0
    sys.stdout.write('(')
    for argument_content in argument:
        count += 1
        print argument_content['Type'], '',
        sys.stdout.write(argument_content['Name'])
        if count < len(argument):
            print ',',
    print (')')


def print_operation(operation):
    """Print a content of an operation
        Arg : A list consists of a content of an operation
    """
    for operation_content in operation:
        if 'diff_tag' in operation_content.keys():
            diff_tag = replace_diff_tag(operation_content['diff_tag'])
            print '    {TAG}'.format(TAG=diff_tag),
        else:
            print '    *',
        if operation_content['ExtAttributes']:
            print_extattributes_of_attribute_and_operation(operation_content['ExtAttributes'])
        print operation_content['Type'],
        if operation_content['Argument']:
            print operation_content['Name'],
            print_argument(operation_content['Argument'])
        else:
            print operation_content['Name']


def print_diff(diff):
    """Print the diff on a shell.
        Arg : A sorted dictionary  
    """
    for interface_name, interface_content in diff.items():
        if 'diff_tag' in interface_content.keys():
            diff_tag = replace_diff_tag(interface_content['diff_tag'])
            print '{TAG}[[{Interface}]]'.format(TAG=diff_tag, Interface=interface_name)
        else:
            print'[[{Interface}]]'.format(Interface=interface_name)
        for member_name, member_content in interface_content.items():
            if member_name == 'ExtAttributes':
                print 'ExtAttributes'
                print_extattribute(member_content)
            elif member_name == 'Const':
                print '  Const'
                print_const(member_content)
            elif member_name == 'Attribute':
                print '  Attribute'
                print_attribute(member_content)
            elif member_name == 'Operation':
                print '  Operation'
                print_operation(member_content)


def make_json_file(data, filepath):
    """Make a json file consiste of dictionary.
        Args : 
            data : A sorted dictionary
            filepath : A file path that we want to make
    """
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
        f.close


def main(argv):
    json_data = argv[0]
    diff_data = load_json_data(json_data)
    sorted_diff = sort_diff_data_by_tags(diff_data)
    make_json_file(sorted_diff, 'sorted.json')
    print_diff(sorted_diff)

if __name__ == '__main__':
    main(sys.argv[1:])
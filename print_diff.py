#!/usr/bin/env python

"""Usage: print_diff.py diff.json
    Print a diff that was gotten by make_diff.py and include idl data.
    Before printting, sort the idl data in alphabetical order or
    by diffing tags that are included in the diff structure.
    diff.json:
        Output of make_diff.py.
        A json file consists of a dictionary expressing a diff between two defferent Chrome versions.
        The structure of the dictionary is like below.
"""

import json
import sys
from collections import OrderedDict


"""Refer to the data structure of input files of make_diff.py for that of this script .
The deffference with the input of make_diff.py is whether diffing tags are included or not.
The diffing tags are included in a parts that has a diff.
    {'Interface': {
            'diff_tag': 'deleted'
            'ExtAttributes': [{'Name': '...'
                               'diff_tag': 'deleted'},
                               ...,
                             ],
            'Consts': [{'Type': '...',
                        'Name': '...',
                        'Value': '...'
                        'diff_tag': 'deleted'},
                        ...,
                      ],
            'Attributes': [{'Type': '...',
                            'Name': '...',
                            'ExtAttributes':[{'Name': '...'},
                                              ...,
                                            ]
                            'diff_tag': 'deleted'},
                            ...,
                          ],
            'Operations': [{'Type': '...',
                            'Name': '...',
                            'ExtAttributes':[{'Name': '...'},
                                              ...,
                                            ],
                            'Arguments': [{'Type': '...',
                                           'Name': '...'},
                                           ...,
                                         ]
                            'diff_tag': 'deleted'},
                            ...,
                          ]
        },
        {
            'ExtAttributes': [{'Name': '...'},
                               ...,
                             ],
            'Consts': [{'Type': '...',
                        'Name': '...',
                        'Value': '...'
                        'diff_tag': 'added'},
                        ...,
                      ],
            'Attributes': [{'Type': '...',
                            'Name': '...',
                            'ExtAttributes':[{'Name': '...'},
                                              ...,
                                            ]},
                            ...,
                          ],
            'Operations': [{'Type': '...',
                            'Name': '...',
                            'ExtAttributes':[{'Name': '...'},
                                              ...,
                                            ],
                            'Arguments': [{'Type': '...',
                                           'Name': '...'},
                                           ...,
                                         ]
                            'diff_tag': 'deleted'},
                            ...,
                           ]
        },
        ...,
    }
"""


EXTATTRIBUTES_AND_MEMBER_TYPES = ['ExtAttributes', 'Consts', 'Attributes', 'Operations']
DIFF_TAG = 'diff_tag'


class Colorize(object):
    def reset_color(self):
        sys.stdout.write('\033[0m')
    def change_color(self, color):
        if color == 'YELLOW':
            sys.stdout.write('\033[33m')
        elif color == 'BLACK':
            sys.stdout.write('\033[30m')
        elif color == 'RED':
            sys.stdout.write('\033[31m')
        elif color == 'GREEN':
            sys.stdout.write('\033[32m')


out = Colorize()


def load_json_data(filepath):
    """Load a json file into a dictionary.
    Args: A file path of a json file that we want to load
    Returns: A "interfaces" that is loaded from the json file
    """
    with open(filepath,'r') as f:
        return json.load(f)


def sort_members(interface):
    sorted_interface = OrderedDict()
    for member_type in EXTATTRIBUTES_AND_MEMBER_TYPES:
        members = interface.get(member_type)
        if members:
            sorted_interface[member_type] = members
    diff_tag = interface.get('diff_tag')
    if diff_tag:
        sorted_interface['diff_tag'] = diff_tag
    return sorted_interface


def sort_interface_names(diff_data):
    """Sort the order of interface names like below.
    [a interface name of "interface" deleted whole
    -> a interface name of "interface" added whole
    -> a interface name of "interface" changed part]
    Args: An "interfaces" that is loaded by load_json_data()
    Returns: 
        changed_whole: 
            A list consists of interface names that are in either newer chrome version or older one.
        changed:
            A list consists of interface names that are in both newer one and older one.
            We need to check whether their members are changed or not later.
    """
    # Following lists are includes interface names
    deleted= []
    added= []
    changed = []
    for interface_name, interface in diff_data.iteritems():
        if DIFF_TAG in interface.keys():
            if interface[DIFF_TAG] == 'deleted':
                deleted.append(interface_name)
            else:
                added.append(interface_name)
        else:
            changed.append(interface_name)
    changed_whole = sorted(deleted) + sorted(added)
    return (changed_whole, sorted(changed))


def sort_members_by_tags(interface):
    """Sort a "members" object by using diff_tag.
    Args: An "interface" object
    Returns: A sorted "interface" object 
    """
    ordered_interface = OrderedDict()
    for member_name, members in interface.iteritems():
        gathered_members = []
        deleted_members = []
        added_members = []
        unchanged_members = []
        for member in members:
            if DIFF_TAG in member.keys():
                if member[DIFF_TAG] == 'deleted':
                    deleted_members.append(member)
                else:
                    added_members.append(member)
            else:
                unchanged_members.append(member)
        for member in deleted_members:
            gathered_members.append(member)
        for member in added_members:
            gathered_members.append(member)
        for member in unchanged_members:
            gathered_members.append(member)
        ordered_interface[member_name] = gathered_members
    return ordered_interface


def sort_diff_data_by_tags(interfaces):
    """Sort an "interfaces" object expressing a diff by using diff_tag.
    Args: An "interfaces" object that is loaded by load_json_data().
    Returns: A sorted "interfaces" object 
    """
    sorted_interfaces = OrderedDict()
    changed_interface = OrderedDict()
    # Following lists (changed_whole, changed_part) are includes sorted interface names
    changed_whole, changed = sort_interface_names(interfaces)
    for interface_name in changed:
        interface = sort_members_by_tags(interfaces[interface_name])
        changed_interface[interface_name] = interface
    for interface_name in changed_whole:
        sorted_interfaces[interface_name] = sort_members(interfaces[interface_name])
    for interface_name, interface in changed_interface.items():
        sorted_interfaces[interface_name] = sort_members(interface)
    return sorted_interfaces


def sort_members_in_alphabetical_order(interface):
    """Sort a "members" object in alphabetical order.
    Args: An "interface" object
    Returns: A sorted "interface" object 
    """
    sorted_interface = OrderedDict()
    for member_type in EXTATTRIBUTES_AND_MEMBER_TYPES:
        member_names = []
        sorted_member_names = OrderedDict()
        sorted_members = []
        for member in interface[member_type]:
            if sorted_members:
                pointer = 0
                for sorted_member in sorted_members:
                    if member['Name'] < sorted_member['Name']:
                        sorted_members.insert(pointer, member)
                        break
                    elif pointer >= (len(sorted_members)-1):
                        sorted_members.append(member)
                    else:
                        pointer += 1
            else:
                sorted_members.append(member)
            sorted_interface[member_type] = sorted_members
    return sorted_interface


def sort_diff_data_in_alphabetical_order(diff):
    """Sort diff in alphabetical order.
    Args: An "interfaces" object that is loaded by load_json_data().
    Returns: A sorted "interfaces" object in alphabetical order
    """
    sorted_diff = OrderedDict(sorted(diff.items(), key=lambda x:x[0]))
    for interface_name, interface in sorted_diff.iteritems():
        sorted_interface = sort_members_in_alphabetical_order(interface)
        if DIFF_TAG in interface:
            sorted_interface[DIFF_TAG] = interface[DIFF_TAG]
        sorted_diff[interface_name] = sorted_interface
    return sorted_diff


def change_color_by_tag(member):
    """Judge whether diff_tag exists or not in an "interface" or a "member"
    and change the color by diffing tag.
    Args:
        member: A "member" object
    """
    if DIFF_TAG in member:
        if member[DIFF_TAG] == 'deleted':
            out.change_color('RED')
            print '-',
        elif member[DIFF_TAG] == 'added':
            out.change_color('GREEN')
            print '+',
    else:
        out.change_color('BLACK')
        print ' ',


def print_extattribute(extattributes):
    """Print extattributes in an "interface".
    Arg: A list consists of a content of an extattributes
    """
    for extattribute in extattributes:
        print '    ',
        change_color_by_tag(extattribute)
        print '{NAME}'.format(NAME=extattribute['Name'])


def print_const(consts):
    """Print consts in an "interface".
    Args: A list consists of a content of consts
    """
    for const in consts:
        print '    ',
        change_color_by_tag(const)
        print '{TYPE}'.format(TYPE=const['Type']),
        print '{NAME}'.format(NAME=const['Name']),
        print '={VALUE}'.format(VALUE=const['Value'])


def print_extattributes_of_member(extattributes):
    """Print extattributes in a Const or an Attribute or an Operation.
    Args: A dictionary of a member whose key is 'ExtAttributes' and value is a list of extattributes
    """
    sys.stdout.write('[')
    count = 0
    for extattribute in extattributes:
        count += 1
        sys.stdout.write(extattribute['Name']) 
        if count < len(extattribute):
            print ', ',
    print ']',


def print_attribute(attributes):
    """Print attributes in an "interface".
    Args: A list consists of a content of attributes
    """
    for attribute in attributes:
        print '    ',
        change_color_by_tag(attribute)
        if attribute['ExtAttributes']:
            print_extattributes_of_member(attribute['ExtAttributes'])
        print attribute['Type'],
        print attribute['Name']


def print_argument(arguments):
    """Print an argument in an operation.
    Args: A dictionary whose key is 'Argument' and value is a list of arguments
    """
    count = 0
    sys.stdout.write('(')
    for argument in arguments:
        count += 1
        print argument['Type'], '',
        sys.stdout.write(argument['Name'])
        if count < len(arguments):
            print ',',
    print (')')


def print_operation(operations):
    """Print a content of an operation
    Args: A list consists of a content of an operation
    """
    for operation in operations:
        print '    ',
        change_color_by_tag(operation)
        if operation['ExtAttributes']:
            print_extattributes_of_member(operation['ExtAttributes'])
        print operation['Type'],
        if operation['Arguments']:
            print operation['Name'],
            print_argument(operation['Arguments'])
        else:
            print operation['Name']


def print_diff(diff, out):
    """Print the diff on a shell.
    Args: A sorted dictionary  
    """
    for interface_name, interface in diff.iteritems():
        change_color_by_tag(interface)
        out.change_color('YELLOW')
        print '[[{Interface}]]'.format(Interface=interface_name)
        for member_name, member in interface.iteritems():
            if member_name == 'ExtAttributes':
                out.reset_color()
                print 'ExtAttributes'
                print_extattribute(member)
            elif member_name == 'Consts':
                out.reset_color()
                print '  Consts'
                print_const(member)
            elif member_name == 'Attributes':
                out.reset_color()
                print '  Attributes'
                print_attribute(member)
            elif member_name == 'Operations':
                out.reset_color()
                print '  Operations'
                print_operation(member)


def make_json_file(data, filepath):
    """Make a json file consists of dictionary.
    Args: 
        data : A sorted dictionary
        filepath : A file path that we want to make
    """
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
        f.close


def main(argv):
    json_data = argv[0]
    the_way_of_sort = argv[1]
    diff_data = load_json_data(json_data)
    if the_way_of_sort == 'TAG':
        tag_sorted_diff = sort_diff_data_by_tags(diff_data)
        make_json_file(tag_sorted_diff, 'sorted.json')
        print_diff(tag_sorted_diff, out)
    elif the_way_of_sort == 'ALPHABET':
        alphabet_sort_diff = sort_diff_data_in_alphabetical_order(diff_data)
        make_json_file(alphabet_sort_diff, 'soted_alphabet.json')
        print_diff(alphabet_sort_diff, out)
    print '\33[0m'


if __name__ == '__main__':
    main(sys.argv[1:])

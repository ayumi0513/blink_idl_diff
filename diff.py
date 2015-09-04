import json
import sys
from collections import OrderedDict


def get_json_data(fname):
    """load a json file into a dictionary"""
    with open(fname,'r') as f:
        return json.load(f)


def get_del_add(target_member1, target_member2,control):
    """
    get a Deleted or Added diff
    target_member1(target_member2) is a list of a target(Attribute,Const,Operation)
    """
    member2_name_list = []
    diff = []
    #if the target_member was originally empty. return it
    if target_member1 != [] and target_member2 == []:
        return target_member1
    #if the target_member1 wasn't empty, return the details in it
    elif target_member1 != [] and target_member2 != []:
        for member_content2 in target_member2:
            member2_name_list.append(member_content2['Name'])
        for member_content1 in target_member1:
            if not member_content1['Name'] in member2_name_list:
                if control == 'Deleted':
                    diff.append({'-':member_content1})
                else:
                    diff.append({'+':member_content1})
    return diff

def get_changes(target_member1, target_member2):
    """
    get a Changed diff
    target_member1(target_member2) is a list of a target(Attribute,Const,Operation)
    """
    member2_dic = {}
    diff = []
    #member_content1(member_content2) is one dictionary of an target(Attribute,Const,Operation)
    #member2_dic is a dictionary whose key is "Name" and value is the dictionary including the key
    if target_member1 != [] and target_member2 != []:
        for member_content2 in target_member2:
            member2_dic[member_content2['Name']] = member_content2
        for member_content1 in target_member1:
            #if a name in member_content1 appears in member_content2 too,
            #check the content that has the name
            if member_content1['Name'] in member2_dic.keys():
                for member_content2 in target_member2:
                    if member_content1['Name'] == member_content2['Name']:
                        if not member_content1 == member_content2:
                            diff_dic = OrderedDict()
                            diff_dic['-'] = member_content2
                            diff_dic['+'] = member_content1
                            diff.append(diff_dic)
    return diff


def make_member_diff(target_member,control,dic1,dic2):
    """Either using the function 'get_del_add' or using the function 'get_changes' dependents on the 'control'""" 
    if not dic1[target_member] == dic2[target_member]:
        if control == 'Deleted' or control == 'Added':
            if get_del_add(dic1[target_member],dic2[target_member],control):
                return  get_del_add(dic1[target_member],dic2[target_member],control)
        elif control == 'Changed':
            if get_changes(dic1[target_member], dic2[target_member]):
                return  get_changes(dic1[target_member], dic2[target_member])


def get_inter(member_diff, dic, pl_mi):
    members = ['ExtAttributes', 'Const', 'Attribute', 'Operation']
    for member in members:
        member_list = []
        for member_content in dic[member]:
            member_list.append({pl_mi:member_content})
        member_diff[member] = member_list
    return member_diff


def get_diff_dict(json_data1, json_data2, control):
    """
    each diff (DeletedInterface, Deleted, AddedInterface, Added, Changed) is gotten individually
    we can decide which diff we would like to get by the parameter 'control'
    """
    output = OrderedDict()
    for interface, dic1 in json_data1.items():
        member_diff = OrderedDict()
        #if a whole interface is changed, add all interface contents to a list "output"
        if not interface in json_data2:
            if control == 'DeletedInterface':
                output[interface] = get_inter(member_diff, dic1, '-')
            elif control == 'AddedInterface':
                output[interface] = get_inter(member_diff, dic1, '+')
        #if there is an interface whose interface name isn't changed,
        #check the contents of the interface
        else:
            if control == 'Deleted' or control == 'Added' or control == 'Changed':
                dic2 = json_data2[interface]
                #if there are some changes in the interface contents,
                #add the data of the interface to a dictionary "member_diff"
                if make_member_diff('ExtAttributes',control,dic1,dic2):
                    member_diff['ExtAttributes'] = make_member_diff('ExtAttributes',control,dic1,dic2)
                if make_member_diff('Const',control,dic1,dic2):
                    member_diff['Const'] = make_member_diff('Const',control,dic1,dic2)
                if make_member_diff('Attribute',control,dic1,dic2):
                    member_diff['Attribute'] = make_member_diff('Attribute',control,dic1,dic2)
                if make_member_diff('Operation',control,dic1,dic2):
                    member_diff['Operation'] = make_member_diff('Operation',control,dic1,dic2)
                if member_diff:
                    output[interface] = member_diff
    return output

def merge_diff_option(diff,a_diff,control):
    """
    option of the function 'merge_diff'
    """
    for interface in a_diff.keys():
        if interface in diff.keys():
            diff[interface][control] = a_diff[interface]
        else:
            diff[interface] = {control:a_diff[interface]}
    return diff


def merge_diff(deleted_interface_diff, deleted_diff, added_interface_diff, added_diff, changed_diff):
    """
    merge five diffs
    """
    diff = OrderedDict()
    merge_diff_option(diff, deleted_interface_diff, 'DeletedInterface')
    merge_diff_option(diff, added_interface_diff, 'AddedInterface')
    merge_diff_option(diff, deleted_diff, 'Deleted')
    merge_diff_option(diff, added_diff, 'Added')
    merge_diff_option(diff, changed_diff, 'Changed')
    return diff



def make_json_file(merged_diff):
    """
    make a json file from merged diff dictionary
    """
    with open('merged_diff.json','w') as f:
        json.dump(merged_diff,f,indent=4)
        f.close



def print_ext(extattributes):
    for extattribute in extattributes:
        for pl_mi, ext_content in extattribute.items():
            for ext in [ext_content]:
                print '    {PL_MI}'.format(PL_MI=pl_mi), 
                print ext['Name']

def print_const(constants):
    for constant in constants:
        for pl_mi, const_content in constant.items():
            for const in [const_content]:
                print '    {PL_MI}'.format(PL_MI=pl_mi),
                print const['Type'],
                print const['Name'],
                print '=', const['Value']


def print_attr(attributes):
    for attribute in attributes:
        for pl_mi, attr_content in attribute.items():
            for attr in [attr_content]:
                sys.stdout.write('    {PL_MI}'.format(PL_MI=pl_mi))
                if attr['ExtAttributes']:
                    sys.stdout.write('[')
                    for ext in attr['ExtAttributes']:
                        sys.stdout.write(ext['Name'])
                    print ']',
                print attr['Type'],
                print attr['Name']


def print_ope(operations):
    for operation in operations:
        for pl_mi, ope_content in operation.items():
            #print '========', ope_content
            for ope in [ope_content]:
                sys.stdout.write('    {PL_MI}'.format(PL_MI=pl_mi)) 
                if ope['ExtAttributes']:
                    sys.stdout.write('[')
                    for ext in ope['ExtAttributes']:
                        sys.stdout.write(' ', ext['Name'])
                    print ']',
                print ope['Type'],
                print ope['Name'],
                if ope['Argument']:
                    count = 0
                    sys.stdout.write('(')
                    for arg in ope['Argument']:
                        count += 1
                        print arg['Type'], '',
                        sys.stdout.write(arg['Name'])
                        if count < len(ope['Argument']):
                            print ',',
                    print ')'


def gather_members(control_contents_list):
    members = OrderedDict()
    ext, const, attr, ope = [], [], [], []
    for control_contents in control_contents_list:
        for member, member_content in control_contents.items():
            if member == 'ExtAttributes':
                ext.append(member_content)
            elif member == 'Const':
                const.append(member_content)
            elif member == 'Attribute':
                attr.append(member_content)
            elif member == 'Operation':
                ope.append(member_content)
    members['ExtAttributes'] = ext
    members['Const'] = const
    members['Attribute'] = attr
    members['Operation'] = ope
    return members


def print_de_ad_ch_diff(members):
    """
    this function's name isn't good.
    this function prints for each member.
    this function's algorithm is mostly the same as print_interface_diff().
    """
    ext_flag, const_flag, attr_flag, ope_flag = 0, 0, 0, 0
    for member_name, member_list in members.items():
        for member in member_list:
            if member_name == 'ExtAttributes':
                if ext_flag == 0:
                    print ' ExtAttributes'
                    ext_flag += 1
                print_ext(member)
            elif member_name == 'Const':
                if const_flag == 0:
                    print '  Const'
                    const_flag += 1
                print_const(member)
            elif member_name == 'Attribute':
                if attr_flag == 0:
                    print '  Attribute'
                    attr_flag +=1
                print_attr(member)
            elif member_name == 'Operation':
                if ope_flag == 0:
                    print '  Operation'
                    ope_flag += 1
                print_ope(member)



def print_interface_diff(diff,pl_mi):
    """
    print for each member
    """
    for member, member_content in diff.items():
        if member_content:
            if member == 'ExtAttributes':
                print ' ExtAttributes'
                print_ext(member_content)
            elif member == 'Const':
                print '  Const'
                print_const(member_content)
            elif member == 'Attribute':
                print '  Attribute'
                print_attr(member_content)
            elif member == 'Operation':
                print '  Operation'
                print_ope(member_content)


def print_diff(merged_diff):
    """
    this function is called in main().
    In this function, we can distinguish from 'DeletedInterface', 'AddedInterface', 'Deleted', 'Added' or 'Changed'.
    If there are 'DeletedInterface' and  'AddedInterface', this function calls print_interface_diff().
    Else, this function calls gather_members() to gather same members included in 'Deleted', 'Added' and 'Changed'.
    And then, calls print_de_ad_ch_diff().
    """
    for interface, interface_contents in merged_diff.items():
        flag = 0
        control_contents_list = []
        for control, control_contents in interface_contents.items():
            if control == 'DeletedInterface':
                print ''
                print '-[[{Interface}]]'.format(Interface=interface)
                print_interface_diff(control_contents, '-')
            elif control == 'AddedInterface':
                print ''
                print '+[[{Interface}]]'.format(Interface=interface)
                print_interface_diff(control_contents, '+')
            elif control == 'Deleted' or control == 'Added' or control == 'Changed':
                if flag == 0:
                    print ''
                    print '[[{Interface}]]'.format(Interface=interface)
                    flag += 1
                control_contents_list.append(control_contents)
        if control_contents_list:
            members = gather_members(control_contents_list)
            print_de_ad_ch_diff(members)


def main(argv):
    new_json = argv[0]
    old_json = argv[1]
    new_json_data = get_json_data(new_json)
    old_json_data = get_json_data(old_json)
    deleted_interface_diff = get_diff_dict(old_json_data, new_json_data, 'DeletedInterface')
    deleted_diff = get_diff_dict(old_json_data, new_json_data, 'Deleted')
    added_interface_diff = get_diff_dict(new_json_data, old_json_data, 'AddedInterface')
    added_diff = get_diff_dict(new_json_data, old_json_data, 'Added')
    changed_diff = get_diff_dict(new_json_data, old_json_data, 'Changed')
    merged_diff = merge_diff(deleted_interface_diff, deleted_diff, added_interface_diff, added_diff, changed_diff)
    make_json_file(merged_diff)
    print_diff(merged_diff)

if __name__ == '__main__':
    main(sys.argv[1:])

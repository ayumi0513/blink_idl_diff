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
                diff.append(member_content1)
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
            if control == 'DeletedInterface' or control == 'AddedInterface':
                print dic1
                member_diff['ExtAttributes'] = dic1['ExtAttributes']
                member_diff['Const'] = dic1['Const']
                member_diff['Attribute'] = dic1['Attribute']
                member_diff['Operation'] = dic1['Operation']
                output[interface] = member_diff
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
    merge_diff_option(diff, deleted_diff, 'Deleted')
    merge_diff_option(diff, added_interface_diff, 'AddedInterface')
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


def print_diff(merged_diff):
    for interface, interface_contents in merged_diff.items():
        for control, control_contents in interface_contents.items():
            if control == 'DeletedInterface':
                print_whole_interface(control_contents)


def print_ext(ext_list, pl_mi):
    print '{PL_MI} ExtAttributes'.format(PL_MI=pl_mi),
    for ext in ext_list:
        print ext['Name']
        print '               ',
    print ''


def print_const(const_list, pl_mi):
    print '  {PL_MI} Const'.format(PL_MI=pl_mi), 
    for const in const_list:
        print const['Type'],
        print const['Name'],
        print ' = ', const['Value']
        print '         ',
    print '' 


def print_attr(attr_list, pl_mi):
    print '  {PL_MI} Attribute'.format(PL_MI=pl_mi),
    for attr in attr_list:
        if attr['ExtAttributes']:
            print '[',
            for ext in attr['ExtAttributes']:
                print ' ', ext['Name'],
            print ']',
        print attr['Type'],
        print attr['Name']
        print '             ',
    print ''


def print_ope(ope_list, pl_mi):
    print '  {PL_MI} Operation'.format(PL_MI=pl_mi),
    for ope in ope_list:
        if ope['ExtAttributes']:
            print '[',
            for ext in ope['ExtAttributes']:
                print ' ', ext['Name'],
            print ']',
        print ope['Type'],
        print ope['Name'],
        if ope['Argument']:
            count = 0
            print '(',
            for arg in ope['Argument']:
                count += 1
                print arg['Type'],
                print '', arg['Name'],
                if count < len(ope['Argument']):
                    print ',',
            print ')'
        print '             ',
    print ''


def print_ext_changed(ext_list):
    for ext_dic in ext_list:
        for pl_mi, ext in ext_dic:
            print '{PL_MI} ExtAttributes'.format(PL_MI=pl_mi),
            print ext['Name']
            print '              ',
        print ''
            
def print_const_changed(const_list):
    #print '===',const_list
    for const_dic in const_list:
        for pl_mi, const in const_dic.items():
            print '  {PL_MI} Const'.format(PL_MI=pl_mi),
            print ' ',const['Type'],
            print ' ',const['Name'],
            print ' = ',const['Value']
            print '       '
        print ''


def print_attr_changed(attr_list):
    for attr_dic in attr_list:
        for pl_mi, attr in attr_dic.items():
            print '  {PL_MI} Attributer'.format(PL_MI=pl_mi),
            if attr['ExtAttributes']:
                print '[',
                for ext in attr['ExtAttributes']:
                    print ' ', ext['Name'],
                print ']',
            print attr['Type'],
            print attr['Name']
            print '             ',
            print ''


def print_ope_changed(ope_list):
    for ope_dic in ope_list:
        for pl_mi, ope in ope_dic.items():
            print '  {PL_MI} Operation'.format(PL_MI=pl_mi),
            if ope['ExtAttributes']:
                print '[',
                for ext in ope['ExtAttributes']:
                    print ' ', ext['Name'],
                    print ']',
            print ope['Type'],
            print ope['Name'],
            if ope['Argument']:
                count = 0
                print '(',
                for arg in ope['Argument']:
                     count += 1
                     print arg['Type'],
                     print '', arg['Name'],
                     if count < len(ope['Argument']):
                         print ',',
                print ')'
            print '             ',
            print ''


def print_diff_option(diff,pl_mi):
    for member, member_content in diff.items():
        if member_content:
            if member == 'ExtAttributes':
                if pl_mi == '-+':
                    print_ext_changed(member_content)
                else:
                    print_ext(member_content, pl_mi)
            elif member == 'Const':
                if pl_mi == '-+':
                    print_const_changed(member_content)
                else:
                    print_const(member_content, pl_mi)
            elif member == 'Attribute':
                if pl_mi == '-+':
                    print_attr_changed(member_content)
                else:
                    print_attr(member_content, pl_mi)
            elif member == 'Operation':
                if pl_mi == '-+':
                    print_ope_changed(member_content)
                else:
                    print_ope(member_content, pl_mi)


def print_diff(merged_diff):
    for interface, interface_contents in merged_diff.items():
        flag = 0
        for control, control_contents in interface_contents.items():
            if control == 'DeletedInterface':
                print '-[[{Interface}]]'.format(Interface=interface)
                print_diff_option(control_contents, '-')
            elif control == 'AddedInterface':
                print '+[[{Interface}]]'.format(Interface=interface)
                print_diff_option(control_contents, '+')
            elif control == 'Deleted' or control == 'Added' or control == 'Changed':
                if flag == 0:
                    print '[[{Interface}]]'.format(Interface=interface)
                    flag += 1
                if control == 'Deleted':
                    print_diff_option(control_contents, '-')
                elif control == 'Added':
                    print_diff_option(control_contents, '+')
                elif control == 'Changed':
                    print_diff_option(control_contents,'-+')

def main(argv):
    new_json = argv[0]
    old_json = argv[1]
    new_json_data = get_json_data(new_json)
    old_json_data = get_json_data(old_json)
    deleted_interface_diff = get_diff_dict(old_json_data, new_json_data, 'DeletedInterface')
    print '       ',deleted_interface_diff
    deleted_diff = get_diff_dict(old_json_data, new_json_data, 'Deleted')
    added_interface_diff = get_diff_dict(new_json_data, old_json_data, 'AddedInterface')
    added_diff = get_diff_dict(new_json_data, old_json_data, 'Added')
    changed_diff = get_diff_dict(new_json_data, old_json_data, 'Changed')
    merged_diff = merge_diff(deleted_interface_diff, deleted_diff, added_interface_diff, added_diff, changed_diff)
    make_json_file(merged_diff)
    print_diff(merged_diff)

if __name__ == '__main__':
    main(sys.argv[1:])

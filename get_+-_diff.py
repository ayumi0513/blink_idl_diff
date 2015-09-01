
import sys
from collections import OrderedDict


def get_json_data(fname):
    """load a json file into a dictionary"""
    with open(fname,'r') as f:
        return json.load(f)


def get_del_add(target_member1, target_member2,control):
    member2_name_list = []
    diff = []
    if target_member1 != [] and target_member2 == []:
        return target_member1
    elif target_member1 != [] and target_member2 != []:
        for member_content2 in target_member2:
            member2_name_list.append(member_content2['Name'])
        if not target_member1 == target_member2:
            for member_content1 in target_member1:
                if not member_content1['Name'] in member2_name_list:
                    if control == 'Deleted':
                        diff.append({'-':member_content1})
                    elif control == 'Added':
                        diff.append({'+':member_content1})
        return diff

#target_member1(target_member2) is a list of a target(Attribute,Const,Operation)
def get_changes(target_member1, target_member2):
    member2_dic = {}
    diff = []
    #member_content1(member_content2) is one dictionary of an target(Attribute,Const,Operation)
    #member2_dic is a dictionary whose key is "Name" and value is the dictionary including the key
    if target_member1 != [] and target_member2 != []:
        for member_content2 in target_member2:
            member2_dic[member_content2['Name']] = member_content2
        if not target_member1 == target_member2:
            for member_content1 in target_member1:
                if member_content1['Name'] in member2_dic.keys():
                    member2_dic_content = member2_dic[member_content1['Name']]
                    for key, value in member_content1.items():
                        if not value == member2_dic_content[key]:
                            diff_dic = OrderedDict()
                            diff_dic['-'] = member2_dic[member_content1['Name']]
                            diff_dic['+'] = member_content1
                            diff.append(diff_dic)
    return diff



def make_member_diff(target_member,control,dic1,dic2):
    if control == 'Deleted' or control == 'Added':
        if get_del_add(dic1[target_member],dic2[target_member],control):
            return  get_del_add(dic1[target_member],dic2[target_member],control)
    elif control == 'Changed':
        if get_changes(dic1[target_member], dic2[target_member]):
            return  get_changes(dic1[target_member], dic2[target_member])



def get_diff_dict(json_data1, json_data2, control):
    output = OrderedDict()
    for interface, dic1 in json_data1.items():
        member_diff = OrderedDict()
        #if a whole interface is changed, add all interface contents to a list "output"
        if not interface in json_data2:
            if control == 'DeletedInterface' or control == 'AddedInterface':
                output[interface] = dic1
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

def merge_diff(deleted_interface_diff, deleted_diff, added_interface_diff, added_diff, changed_diff):
    diff = OrderedDict()
    for interface in deleted_interface_diff.keys():
        diff[interface] = {'DeletedInterface':deleted_interface_diff[interface]}
    for interface in deleted_diff.keys():
        if interface in diff.keys():
            diff[interface]['Deleted'] = deleted_diff[interface]
        else:
            diff[interface] = {'Deleted':deleted_diff[interface]}
    for interface in added_interface_diff.keys():
        if interface in diff.keys():
            diff[interface]['AddedInterface'] = added_interface_diff[interface]
        else:
            diff[interface] = {'AddedInterface':added_interface_diff[interface]}
    for interface in added_diff.keys():
        if interface in diff.keys():
            diff[interface]['Added'] = added_diff[interface]
        else:
            diff[interface] = {'Added':added_diff[interface]}
    for interface in changed_diff.keys():
        if interface in diff.keys():
            diff[interface]['Changed'] = changed_diff[interface]
        else:
            diff[interface] = changed_diff[interface]
    return diff



def make_json_file(merged_diff):
    with open('merged_diff.json','w') as f:
        json.dump(merged_diff,f,indent=4)
        f.close

def print_diff_option_option(contents, pl_mi, control):
    for content in contents:
        if control == 'AddedInterface' or control == 'DeletedInterface':
            for key, value in content.items():
                if key == 'Argument' or key == 'ExtAttributes':
                    print '    {Pl_Mi}'.format(Pl_Mi=pl_mi), key
                    for val in value:
                        for k, v in val.items():
                            print '      {Pl_Mi}'.format(Pl_Mi=pl_mi), k,
                            print '  ', v
                else:
                    print '    {Pl_Mi}'.format(Pl_Mi=pl_mi), key,
                    print '  ', value
        else:
            for con in content.values():
                for key, value in con.items():
                    if key == 'Argument': 
                        print '    {Pl_Mi}'.format(Pl_Mi=pl_mi), key
                        for val in value:
                            for k, v in val.items():
                                print '      {Pl_Mi}'.format(Pl_Mi=pl_mi), k,
                                print ' : ', v
                    elif key == 'ExtAttributes':
                        #print '{Pl_Mi}'.format(Pl_Mi=pl_mi), key
                        for val in value:
                            for k, v in val.items():
                                print '{Pl_Mi}'.format(Pl_Mi=pl_mi), k,
                                print ' : ', v
                    else:
                         print '    {Pl_Mi}'.format(Pl_Mi=pl_mi), key,
                         print ' : ', value


def print_diff_option(member, contents, pl_mi, control):
    if member == 'Name' or member == 'FilePath':
        print '  {Pl_Mi}'.format(Pl_Mi=pl_mi), member,
        print ' : ', contents
    else:
        if member == 'ExtAttributes':
            print '{Pl_Mi}'.format(Pl_Mi=pl_mi), member
        else:
            print '  {Pl_Mi}'.format(Pl_Mi=pl_mi), member
        print_diff_option_option(contents, pl_mi, control)



def print_changed_diff(member, contents):
    print '   ', member
    for content in contents:
        for pl_mi, changed in content.items():
            if pl_mi == '-':  
                print '      -',
            elif pl_mi == '+':
                print '      +',
            for key, value in changed.items():
                if key == 'Argument' or key == 'ExtAttributes':
                    print key,
                    for val in value:
                        for k,v in val.items():
                            print k,
                            print ' : ',v,
                else:
                    print key,
                    print ' : ',value,
            print ' '



def print_diff(merged_diff):
    flag = 0
    for interface, interface_contents in merged_diff.items():
        for control, control_contents in interface_contents.items():
            if control == 'AddedInterface':
                print '+','[[{Interface}]]'.format(Interface=interface)
                for member, contents in control_contents.items():
                    print_diff_option(member, contents, '+','AddedInterface')
            elif control == 'DeletedInterface':
                print '-', '[[{Interface}]]'.format(Interface=interface)
                for member, contents in control_contents.items():
                    print_diff_option(member, contents, '-','DeletedInterface')
            elif control == 'Added':
                if flag == 0:
                    print '[[{Interface}]]'.format(Interface=interface)
                    flag = 1
                for member, contents in control_contents.items():
                    print_diff_option(member, contents, '+','Added')
            elif control == 'Deleted':
                if flag == 0:
                    print '[[{Interface}]]'.format(Interface=interface)
                    flag = 1
                for member, contents in control_contents.items():
                    print_diff_option(member, contents, '-','Deleted')
            elif control == 'Changed':
                if flag == 0:
                    print '[[{Interface}]]'.format(Interface=interface)
                    flag = 1
                for member, contents in control_contents.items():
                    print_changed_diff(member, contents)


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

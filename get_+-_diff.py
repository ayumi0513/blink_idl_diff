import json
import sys

new_json = 'json_dict1.json'
old_json = 'json_dict2.json'


def get_json_data(fname):
    """load a json file into a dictionary"""
    with open(fname,'r') as f:
        return json.load(f)


def get_del_add(target_member1, target_member2):
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
                    diff.append(member_content1)
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
                            diff.append({'+':member_content1,'-': member2_dic[member_content1['Name']]})
    return diff



def make_member_diff(target_member,control,dic1,dic2):
    if control == 'Deleted' or control == 'Added':
        if get_del_add(dic1[target_member],dic2[target_member]):
            return  get_del_add(dic1[target_member],dic2[target_member])
    elif control == 'Changed':
        if get_changes(dic1[target_member], dic2[target_member]):
            return  get_changes(dic1[target_member], dic2[target_member])



def get_diff_dict(json_data1, json_data2, control):
    output = {}
    diff = {}
    if control == 'Deleted' or control == 'DeletedInterface':
        tmp = json_data2
        json_data2 = json_data1
        json_data1 = tmp
    for interface, dic1 in json_data1.items():
        member_diff = {}
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
                if make_member_diff('Attribute',control,dic1,dic2):
                    member_diff['Attribute'] = make_member_diff('Attribute',control,dic1,dic2)
                if make_member_diff('Const',control,dic1,dic2):
                    member_diff['Const'] = make_member_diff('Const',control,dic1,dic2)
                if make_member_diff('ExtAttributes',control,dic1,dic2):
                    member_diff['ExtAttributes'] = make_member_diff('ExtAttributes',control,dic1,dic2)
                if make_member_diff('Operation',control,dic1,dic2):
                    member_diff['Operation'] = make_member_diff('Operation',control,dic1,dic2)
                if member_diff:
                    output[interface] = member_diff
    return output

def merge_diff(added_diff,deleted_diff,changed_diff):
    diff ={}
    tmp = {}
    for interface1 in deleted_diff.keys():
        if not interface1 in deleted_diff.keys():
            diff[interface1] = deleted_diff[interface1]
    for interface2 in added_diff.keys():
        if not interface2 in added_diff.keys():
            diff[interface2] = added_diff[interface2]
    for interface3 in changed_diff.keys():
        if interface3 in added_diff.keys():
            tmp =  added_diff[interface2]
            tmp['Deleted'] = deleted_diff[interface2]['Deleted']
            diff[interface2] = tmp
        elif not interface2 in added_diff.keys():
            diff[interface2] = deleted_diff[interface2]
    return diff



def make_json_file(merged_diff):
    with open('merged_diff.json','w') as f:
        json.dump(merged_diff,f,indent=4)
        f.close

def print_diff_option(member, contents, pl_mi):
    if member == 'Name' or member == 'FilePath':
        print '  {Pl_Mi}'.format(Pl_Mi=pl_mi), member,
        print ' : ', contents
    else:
        print '  {Pl_Mi}'.format(Pl_Mi=pl_mi), member
        for content in contents:
            for key, value in content.items():
                if key == 'Argument' or key == 'ExtAttributes':
                    print '    {Pl_Mi}'.format(Pl_Mi=pl_mi), key
                    for val in value:
                        for k, v in val.items():
                            print '      {Pl_Mi}'.format(Pl_Mi=pl_mi), k,
                            print ' : ', v
                else:
                    print '    {Pl_Mi}'.format(Pl_Mi=pl_mi), key,
                    print ' : ', value

def print_changed_diff(member, contents):
    print '   ', member
    for content in contents:
        for pl_mi, changed in content.items():
            if pl_mi == '+':  
                print '      +',
            elif pl_mi == '-':
                print '      -',
            for key, value in changed.items():
                print key,
                print ' : ',value,
            print ' '


def print_diff(merged_diff):
    for interface, interface_contents in merged_diff.items():
        for add_cha_del, add_cha_del_contents in interface_contents.items():
            if add_cha_del == 'AddedInterface':
                print '+','[[{Interface}]]'.format(Interface=interface)
                for member, contents in add_cha_del_contents.items():
                    print_diff_option(member, contents, '+')
            elif add_cha_del == 'DeletedInterface':
                print '-', '[[{Interface}]]'.format(Interface=interface)
                for member, contents in add_cha_del_contents.items():
                    print_diff_option(member, contents, '-')
            elif add_cha_del == 'Add':
                print '[[{Interface}]]'.format(Interface=interface)
                for member, contents in add_cha_del_contents.items():
                    print_diff_option(member, contents, '+')
            elif add_cha_del == 'Del':
                for member, contents in add_cha_del_contents.items():
                    print_diff_option(member, contents, '-')
            elif add_cha_del == 'Changed':
                for member, contents in add_cha_del_contents.items():
                    print_changed_diff(member, contents)


def main(argv):
    new_json_data = get_json_data(new_json)
    old_json_data = get_json_data(old_json)
    deleted_interface_diff = get_diff_dict(new_json_data, old_json_data, 'DeletedInterface')
    deleted_diff = get_diff_dict(new_json_data, old_json_data, 'Deleted')
    added_interface_diff = get_diff_dict(new_json_data, old_json_data, 'AddedInterface')
    added_diff = get_diff_dict(new_json_data, old_json_data, 'Added')
    changed_diff = get_diff_dict(new_json_data, old_json_data, 'Changed')
    print 'Changed', changed_diff
    print ''
    print 'DeletedInterface', deleted_interface_diff
    print ''
    print 'Deleted',deleted_diff
    print ''
    print 'AddedInterface', added_interface_diff
    print ''
    print 'Added',added_diff
    print ''
    #merged_diff = merge_diff(added_diff, deleted_diff,changed_diff)
    #make_json_file(merged_diff)
    #print_diff(merged_diff) 

if __name__ == '__main__':
    main(sys.argv[1:])

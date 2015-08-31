import json
import sys

new_json = 'json_dict1.json'
old_json = 'json_dict2.json'


def get_json_data(fname):
    """load a json file into a dictionary"""
    with open(fname,'r') as f:
        return json.load(f)


def get_members_diff(target_member1, target_member2):
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

#target_member1(target_member2) is a list of an target(Attribute,Const,Operation)
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



def get_diff_dict(json_data1, json_data2, control):
    output = {}
    diff = {}
    if control == 'Deleted':
        tmp = json_data2
        json_data2 = json_data1
        json_data1 = tmp
    for interface, dic1 in json_data1.items():
        add, changed, dele = {}, {}, {}
        #if a whole interface is changed, add all interface contents to a list "output"
        if not interface in json_data2:
            if control == 'Add_or_Chan':
                output[interface] = {'AddedInterface':dic1}
            else:
                output[interface] = {'DeletedInterface':dic1}
        #if there is a interface whose interface name isn't changed,
        #check the contents of the interface
        else:
            dic2 = json_data2[interface]
            #if there are some changes in the interface contents,
            #add a key and value to a dictionary "interface_diff"
            if get_members_diff(dic1['Attribute'], dic2['Attribute']):
                if control == 'Add_or_Chan':
                    add['Attribute'] = get_members_diff(dic1['Attribute'], dic2['Attribute'])
                    if get_changes(dic1['Attribute'], dic2['Attribute']):
                        changed['Attribute'] = get_changes(dic1['Attribute'], dic2['Attribute'])
                else:
                    dele ['Attribute'] = get_members_diff(dic1['Attribute'], dic2['Attribute'])
            if get_members_diff(dic1['Const'], dic2['Const']):
                if control == 'Add_or_Chan':
                    add['Const'] = get_members_diff(dic1['Const'], dic2['Const'])
                    if get_changes(dic1['Const'], dic2['Const']):
                        changed['Const'] = get_changes(dic1['Const'], dic2['Const'])
                else:
                    dele['Const'] = get_members_diff(dic1['Const'], dic2['Const'])
            if get_members_diff(dic1['ExtAttributes'], dic2['ExtAttributes']):
                if control == 'Add_or_Chan':
                    add['ExtAttributes'] = get_members_diff(dic1['ExtAttributes'], dic2['ExtAttributes'])
                    if get_changes(dic1['ExtAttributes'], dic2['[ExtAttributes']):
                        changed['ExtAttributes'] = get_changes(dic1['ExtAttributes'], dic2['ExtAttributes'])
                else:
                    dele['ExtAttributes'] = get_members_diff(dic1['ExtAttributes'], dic2['ExtAttributes'])
            if get_members_diff(dic1['Operation'], dic2['Operation']):
                if control == 'Add_or_Chan':
                    add['Operation'] = get_members_diff(dic1['Operation'], dic2['Operation'])
                    if get_changes(dic1['Operation'], dic2['Operation']):
                        changed['Operation'] = get_changes(dic1['Operation'], dic2['Operation'])
                else:
                    dele['Operation'] = get_members_diff(dic1['Operation'], dic2['Operation'])
            #if interface_diff not empty(that means there are some changes),
            #add the interface_diff to a list "output"
            if control == 'Add_or_Chan'and add != {} and changed != {}:
                diff['Add'] = add
                diff['Changed'] = changed
                output[interface] = diff
            elif control == 'Deleted' and dele != {}:
                diff['Del'] = dele
                output[interface] = diff
    return output

def merge_diff(added_diff,deleted_diff):
    diff ={}
    tmp = {}
    for interface1 in added_diff.keys():
        if not interface1 in deleted_diff.keys():
            diff[interface1] = added_diff[interface1]
    for interface2 in deleted_diff.keys():
        if interface2 in added_diff.keys():
            tmp =  added_diff[interface2]
            tmp['Del'] = deleted_diff[interface2]['Del']
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
        print '  ', contents
    else:
        print '  {Pl_Mi}'.format(Pl_Mi=pl_mi), member
        for content in contents:
            for key, value in content.items():
                if key == 'Argument':
                    print '    {Pl_Mi}'.format(Pl_Mi=pl_mi), key
                    for val in value:
                        for k, v in val.items():
                            print '      {Pl_Mi}'.format(Pl_Mi=pl_mi), k,
                            print '  ', v
                else:
                    print '    {Pl_Mi}'.format(Pl_Mi=pl_mi), key,
                    print '  ', value

def print_changed_diff(member, contents):
    print '   ', member
    for content in contents:
        for pl_mi, changed in content.items():
            pl_line = []
            for key, value in changed.items():
                if pl_mi == '+':
                    #pl_line = make_line_output(key,value)
                    print '      +', key,
                    print '        ',value
                if pl_mi == '-':
                    print '      -', key,
                    print '         ', value
            #print pl_line

def make_line_output(key,value):
    line = []
    #return_string = key + value
    line.append(key + value)
    return line


def print_diff(merged_diff):
    for interface, add_cha_del in merged_diff.items():
        if 'AddedInterface' in add_cha_del.keys():
            print '+','[[{Interface}]]'.format(Interface=interface)
            for member, contents in add_cha_del['AddedInterface'].items():
                print_diff_option(member, contents, '+')
        if 'DeletedInterface' in add_cha_del.keys():
            print '-', '[[{Interface}]]'.format(Interface=interface)
            for member, contents in add_cha_del['DeletedInterface'].items():
                print_diff_option(member, contents, '-')
        if 'Add' in add_cha_del.keys() or 'Del' in add_cha_del.keys() or 'Changed' in add_cha_del.keys():
            print '[[{Interface}]]'.format(Interface=interface)
            if 'Add' in add_cha_del.keys():
                for member, contents in add_cha_del['Add'].items():
                    print_diff_option(member, contents, '+')
            if 'Del' in add_cha_del.keys():
                for member, content in add_cha_del['Del'].items():
                    print_diff_option(member, contents, '-')
            if 'Changed' in add_cha_del.keys():
                for member, contents in add_cha_del['Changed'].items():
                    print_changed_diff(member, contents)


def main(argv):
    new_json_data = get_json_data(new_json)
    old_json_data = get_json_data(old_json)
    added_diff = get_diff_dict(new_json_data, old_json_data, 'Add_or_Chan')
    deleted_diff = get_diff_dict(new_json_data, old_json_data, 'Deleted')
    merged_diff = merge_diff(added_diff, deleted_diff)
    make_json_file(merged_diff)
    print_diff(merged_diff) 

if __name__ == '__main__':
    main(sys.argv[1:])

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


def get_changes(target_member1, target_member2):
    member2_dic = {}
    diff = []
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
    if control == 'Del':
        tmp = json_data2
        json_data2 = json_data1
        json_data1 = tmp
    for interface, dic1 in json_data1.items():
        add, changed, dele = {}, {}, {}
        #if a whole interface is changed, add all interface contents to a list "output"
        if not interface in json_data2:
            output[interface] = {'InterfaceChange':dic1}
        #if there is a interface whose interface name isn't changed,
        #check the contents of the interface
        else:
            dic2 = json_data2[interface]
            #if there are some changes in the interface contents,
            #add a key and value to a dictionary "interface_diff"
            if get_members_diff(dic1['Attribute'], dic2['Attribute']):
                if control == 'Add_or_Chan':
                    add['Attribute'] = get_members_diff(dic1['Attribute'], dic2['Attribute'])
                    changed['Attribute'] = get_changes(dic1['Attribute'], dic2['Attribute'])
                else:
                    dele ['Attribute'] = get_members_diff(dic1['Attribute'], dic2['Attribute'])
            if get_members_diff(dic1['Const'], dic2['Const']):
                if control == 'Add_or_Chan':
                    add['Const'] = get_members_diff(dic1['Const'], dic2['Const'])
                    changed['Const'] = get_changes(dic1['Const'], dic2['Const'])
                else:
                    dele['Const'] = get_members_diff(dic1['Const'], dic2['Const'])
            if get_members_diff(dic1['ExtAttributes'], dic2['ExtAttributes']):
                if control == 'Add_or_Chan':
                    add['ExtAttributes'] = get_members_diff(dic1['ExtAttributes'], dic2['ExtAttributes'])
                    changed['ExtAttributes'] = get_changes(dic1['ExtAttributes'], dic2['ExtAttributes'])
                else:
                    dele['ExtAttributes'] = get_members_diff(dic1['ExtAttributes'], dic2['ExtAttributes'])
            if get_members_diff(dic1['Operation'], dic2['Operation']):
                if control == 'Add_or_Chan':
                    add['Operation'] = get_members_diff(dic1['Operation'], dic2['Operation'])
                    changed['Operation'] = get_changes(dic1['Operation'], dic2['Operation'])
                else:
                    dele['Operation'] = get_members_diff(dic1['Operation'], dic2['Operation'])
            #if interface_diff not empty(that means there are some changes),
            #add the interface_diff to a list "output"
            if control == 'Add_or_Chan'and add != {}:
                diff['Add'] = add
                diff['Del'] = dele
                diff['Changed'] = changed
                output[interface] = diff
            elif control == 'Deleted' and dele != {}:
                diff['Del'] = dele
                output[interface] = diff
    print output
    return output



def make_json_file(added_diff, deleted_diff):
    diff = {}
    diff['===Added==='] = added_diff
    diff['===Deleted==='] = deleted_diff
    with open('new_diff.json','w') as f:
        json.dump(diff,f,indent=4)
        f.close

def main(argv):
    new_json_data = get_json_data(new_json)
    old_json_data = get_json_data(old_json)
    added_diff = get_diff_dict(new_json_data, old_json_data, 'Add_or_Chan')
    #print added_diff
    #deleted_diff = get_diff_dict(old_json_data, new_json_data, 'Del')
    #print '================='
    #print deleted_diff
    #make_json_file(added_diff, deleted_diff)

if __name__ == '__main__':
    main(sys.argv[1:])

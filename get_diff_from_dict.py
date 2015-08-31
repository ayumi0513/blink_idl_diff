import json
import sys

new_json = 'json_dict1.json'
old_json = 'json_dict2.json'


def get_json_data(fname):
    """load a json file into a dictionary"""
    with open(fname,'r') as f:
        return json.load(f)

def get_interface_diff(new_json_data,old_json_data):
    output = []
    for key in new_json_data.keys():
        if not key in old_json_data:
            output.append(key)
    return output


def get_ope_change_detail(part_of_operation1,operation2):
    flag = 0
    ope_diff = {}
    ext, arg  = [], []
    ope_diff['Name'] = part_of_operation1['Name']
    #look for the operation name which equivalent to the operation name of "part_of_operation1" in "operation2"
    for part_of_operation2 in operation2:
        if part_of_operation2['Name'] == part_of_operation1['Name']:
            #if find the same operation name, change the flag number from 0 to 1
            flag = 1
            if not part_of_operation1['Type'] == part_of_operation2['Type']:
                ope_diff['Type'] = part_of_operation1['Type']
            elif not part_of_operation1['ExtAttributes'] == part_of_operation2['ExtAttributes']:
                for ext1 in part_of_operation1['ExtAttributes']:
                    if not ext1 in part_of_operation2['ExtAttributes']:
                        ext.append(ext1['Name'])
            elif not part_of_operation2['Argument'] == part_of_operation1['Argument']:
                for arg1 in part_of_operation1['Argument']:
                    if not arg1 in part_of_operation2['Argument']:
                        arg.append({'Type':arg1['Type'],'Name':arg1['Name']})
    #if the flag is still 0
    #(that means there is not the operation ("part_of_operation1") in "operation2"),
    #return the all operation contents 
    if flag == 0:
        return part_of_operation1
        #ope_diff['Name'] = part_of_operation1['Name']
        #ope_diff['Type'] = part_of_operation1['Type']
    #if there are some changes in the operation("part_of_operation1"),
    #add the name of operaiton to "ope_diff" and return it
    elif ope_diff:
        if ext:
            ope_diff['ExtAttributes'] = ext
        if arg:
            ope_diff['Argument'] = arg
        return ope_diff

def get_change_detail(dic1,dic2,target_member):
    """compare two contents(value) of an interface which have same interface name"""
    member_diff = []
    if not dic1[target_member] == dic2[target_member]:
        #if the place of the interface is changed, return the path of file "dic1['FilePath']"
        if target_member == 'FilePath':
            return {'FilePath':dic1['FilePath']}
        else:
            #check whether the part of the target_member of dic1 is included the target_member of dic2
            for part_of_member in dic1[target_member]:
                if not part_of_member in dic2[target_member]:
                    if target_member == 'Attribute':
                        attr = {}
                        attr['Type'] = part_of_member['Type']
                        attr['Name'] = part_of_member['Name']
                        member_diff.append(attr)
                    elif target_member == 'Const':
                        cns = {}
                        cns['Type'] = part_of_member['Type']
                        cns['Name'] = part_of_member['Name']
                        cns['Value'] = part_of_member['Value']
                        member_diff.append(cns)
                    elif target_member == 'ExtAttributes':
                        ext = {}
                        ext['Name'] = part_of_member['Name']
                        member_diff.append(ext)
                    elif target_member == 'Operation':
                        ope = get_ope_change_detail(part_of_member,dic2[target_member])
                        member_diff.append(ope)
    return member_diff
   
def get_ope_change(part_of_operation1,operation2):
    flag = 0
    for part_of_operation2 in operation2:
        if part_of_operation2['Name'] == part_of_operation1['Name']:
            flag = 1
            if not part_of_operation1 == part_of_operation2:
                return part_of_operation1
    if flag == 0:
        return part_of_operation1
    else:
        return {}

def get_change(dic1,dic2,target_member):
    member_diff = []
    if not dic1[target_member] == dic2[target_member]:
        if target_member == 'FilePath':
            return {'FilePath':dic1['FilePath']}
        else:
            for part_of_member in dic1[target_member]:
                if not part_of_member in dic2[target_member]:
                    if target_member == 'Operation':
                        member_diff.append(get_ope_change(part_of_member,dic2[target_member]))
                    else:
                        member_diff.append(part_of_member)
    return member_diff



def get_diff_dict(json_data1,json_data2):
    output = {}
    diff = {}
    for interface, dic1 in json_data1.items():
        interface_diff = {}
        changed, changed_detail = {}, {}
        #if a whole interface is changed, add all interface contents to a list "output"
        if not interface in json_data2:
            output[interface] = {'InterfaceChange':dic1}
        #if there is a interface whose interface name isn't changed,
        #check the contents of the interface
        else:
            dic2 = json_data2[interface]
            #if there are some changes in the interface contents,
            #add a key and value to a dictionary "interface_diff"
            if get_change_detail(dic1,dic2,'FilePath'):
                changed['FilePath'] = get_change(dic1,dic2,'FilePath')
                changed_detail['FilePath'] = get_change_detail(dic1,dic2,'FilePath')
            if get_change_detail(dic1,dic2,'Attribute'):
                changed['Attribute'] = get_change(dic1,dic2,'Attribute')
                changed_detail['Attribute'] = get_change_detail(dic1,dic2,'Attribute')
            if get_change_detail(dic1,dic2,'Const'):
                changed['Const'] = get_change(dic1,dic2,'Const')
                changed_detail['Const'] = get_change_detail(dic1,dic2,'Const')
            if get_change_detail(dic1,dic2,'ExtAttributes'):
                changed['ExtAttributes'] = get_change(dic1,dic2,'ExtAttributes')
                changed_detail['ExtAttributes'] = get_change_detail(dic1,dic2,'ExtAttributes')
            if get_change(dic1,dic2,'Operation') and get_change_detail(dic1,dic2,'Operation'):
                changed['Operation'] = get_change(dic1,dic2,'Operation')
                changed_detail['Operation'] = get_change_detail(dic1,dic2,'Operation')
            #if interface_diff not empty(that means there are some changes),
            #add the interface_diff to a list "output"
            if changed:
                diff['Change'] = changed
                diff['ChangeDetail'] = changed_detail
                output[interface] = diff
    return output


def print_diff_option(whole_or_part,detail):
    print '   ', 
    print '|',whole_or_part,'|'
    for member, member_contents in detail.items():
        print '------',
        print member,'------'
        if type(member_contents) is list:
            for member_content in member_contents:
                print '        -----'
                for key, values in member_content.items():
                    if key == 'Argument':
                        for value in values:
                            print '        ',
                            print key
                            for arg_key, arg_value in value.items():
                                print '          ',
                                print arg_key,
                                print arg_value
                    else:
                        print '        ',
                        print key,
                        print values
        else:
            print '        ',
            print member_contents



def print_diff(diff_dict,add_or_delete):
    print add_or_delete
    for interface, interface_contents in diff_dict.items():
        print '[[{Interface}]]'.format(Interface=interface)
        changed_detail = {}
        for whole_or_part, detail in interface_contents.items():
            if whole_or_part == 'Change':
                print_diff_option('Change',detail)
            elif whole_or_part == 'InterfaceChange':
                print_diff_option('InterfaceChange',detail)
            else:
                changed_detail = detail
        if changed_detail:
            print_diff_option('ChangeDetail',changed_detail)


def make_json_file(added_diff,deleted_diff):
    diff = {}
    diff['===Added==='] = added_diff
    diff['===Deleted==='] = deleted_diff
    with open('diff.json','w') as f:
        json.dump(diff,f,indent=4)
        f.close

def main(argv):
    new_json_data = get_json_data(new_json)
    old_json_data = get_json_data(old_json)
    added_diff = get_diff_dict(new_json_data,old_json_data)
    deleted_diff = get_diff_dict(old_json_data,new_json_data)
    print_diff(added_diff,'===Added===')
    print_diff(deleted_diff,'===Deleted===')
    make_json_file(added_diff,deleted_diff)
if __name__ == '__main__':
    main(sys.argv[1:])

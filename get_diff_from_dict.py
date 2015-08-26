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


def operation_diff(part_of_operation1,operation2):
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
        ope_diff['Name'] = part_of_operation1['Name']
        if ext:
            ope_diff['ExtAttributes'] = ext
        if arg:
            ope_diff['Argument'] = arg
        return ope_diff

def compare_data(dic1,dic2,target_member):
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
                        member_diff.append({'Type':part_of_member['Type'],'Name':part_of_member['Name']})
                    elif target_member == 'Const':
                        member_diff.append({'Type':part_of_member['Type'],'Name':part_of_member['Name'],'Value':part_of_member['Value']})
                    elif target_member == 'ExtAttributes':
                        member_diff.append({'Name':part_of_member['Name']})
                    elif target_member == 'Operation':
                        member_diff.append(operation_diff(part_of_member,dic2[target_member]))
    return member_diff
   


def get_diff_dict(json_data1,json_data2):
    output = {}
    for interface, dic1 in json_data1.items():
        interface_diff = {}
        #if a whole interface is changed, add all interface contents to a list "output"
        if not interface in json_data2:
            output[interface] = dic1
        #if there is a interface whose interface name isn't changed, check the contents of the interface
        else:
            dic2 = json_data2[interface]
            #if there are some changes in the interface contents, add a key and value to a dictionary "interface_diff"
            if compare_data(dic1,dic2,'FilePath'):
                interface_diff['FilePath'] = compare_data(dic1,dic2,'FilePath')
            if compare_data(dic1,dic2,'Attribute'):
                interface_diff['Attribute'] = compare_data(dic1,dic2,'Attribute')
            if compare_data(dic1,dic2,'Const'):
                interface_diff['Const'] = compare_data(dic1,dic2,'Const')
            if compare_data(dic1,dic2,'ExtAttributes'):
                interface_diff['ExtAttributes'] = compare_data(dic1,dic2,'ExtAttributes')
            if compare_data(dic1,dic2,'Operation'):
                interface_diff['Operation'] = compare_data(dic1,dic2,'Operation')
            #if interface_diff not empty(that means there are some changes),
            #add the interface name to a dictionary "interface_diff"
            #and add the interface_diff to a list "output"
            if interface_diff:
              interface_diff['Name'] = dic1['Name']
              output[interface] = interface_diff
    return output


def print_diff(diff_dict,add_or_delete):
    print add_or_delete
    for interface, content in diff_dict.items():
        print '[[{Interface}]]'.format(Interface=interface)
        print content



def main(argv):
    new_json_data = get_json_data(new_json)
    #print new_json_data
    old_json_data = get_json_data(old_json)
    #print old_json_data
    added_diff = get_diff_dict(new_json_data,old_json_data)
    deleted_diff = get_diff_dict(old_json_data,new_json_data)
    print_diff(added_diff,'===Added===')
    print_diff(deleted_diff,'===Deleted===')


if __name__ == '__main__':
    main(sys.argv[1:])

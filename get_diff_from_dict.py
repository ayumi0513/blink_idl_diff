import json
import sys

new_json = 'json_dict1.json'
old_json = 'json_dict2.json'


def get_json_data(fname):
    """load a json file into a dictionary"""
    f = open(fname,'r')
    json_data = json.load(f)
    f.close()
    return json_data
    
    #with open(fname,'r') as f:
        #return json.load(f)

def get_interface_diff(new_json_data,old_json_data):
    output = []
    for key in new_json_data.keys():
        if not key in old_json_data:
            output.append(key)
    return output


def operation_diff(operation_content1,operation2):
    flag = 0
    ope_diff = {}
    ext, arg  = [], []
    ope_diff['Name'] = operation_content1['Name']
    for operation_content2 in operation2:
        if operation_content2['Name'] == operation_content1['Name']:
            flag = 1
            if not operation_content2['Type'] == operation_content1['Type']:
                ope_diff['Type'] = operation_content1['Type']
            elif not operation_content2['ExtAttributes'] == operation_content1['ExtAttributes']:
                for ext1 in operation_content1['ExtAttributes']:
                    if not ext1 in operation_content2['ExtAttributes']:
                        ext.append(ext1['Name'])
            elif not operation_content2['Argument'] == operation_content1['Argument']:
                for arg1 in operation_content1['Argument']:
                    if not arg1 in operation_content2['Argument']:
                        arg.append({'Type':arg1['Type'],'Name':arg1['Name']})
    if flag == 0:
        ope_diff['Name'] = operation_content1['Name']
        ope_diff['Type'] = operation_content1['Type']
    ope_diff['ExtAttributes'] = ext
    ope_diff['Argument'] = arg
    return ope_diff

def compare_data(dic1,dic2,target_member):
    """compare two contents(value) of an interface which have same interface name"""
    member_diff = []
    if not dic1[target_member] == dic2[target_member]:
        if target_member == 'FilePath':
            return {'FilePath':dic1['FilePath']}
        else:
            for member_content in dic1[target_member]:
                if not member_content in dic2[target_member]:
                    if target_member == 'Attribute':
                        member_diff.append({'Type':member_content['Type'],'Name':member_content['Name']})
                    elif target_member == 'Const':
                        member_diff.append({'Type':member_content['Type'],'Name':member_content['Name'],'Value':member_content['Value']})
                    elif target_member == 'ExtAttributes':
                        member_diff.append({'Name':member_content['Name']})
                    elif target_member == 'Operation':
                        member_diff.append(operation_diff(member_content,dic2[target_member]))
    return member_diff
    


def get_diff_list(json_data1,json_data2):
    output = {}
    for interface, dic1 in json_data1.items():
        interface_diff = {}
        if not interface in json_data2:
            #interface_diff['Name'] = dic1['Name']
            #interface_diff['Path'] = dic1['FilePath']
            #output[interface] = interface_diff
            output[interface] = dic1
        else:
            dic2 = json_data2[interface]
            interface_diff['Name'] = dic1['Name']
            interface_diff['FilePath'] = compare_data(dic1,dic2,'FilePath')
            interface_diff['Attribute'] = compare_data(dic1,dic2,'Attribute')
            interface_diff['Const'] = compare_data(dic1,dic2,'Const')
            interface_diff['ExtAttributes'] = compare_data(dic1,dic2,'ExtAttributes')
            interface_diff['Operation'] = compare_data(dic1,dic2,'Operation')
            output[interface] = interface_diff
    return output


def main(argv):
    new_json_data = get_json_data(new_json)
    #print new_json_data
    old_json_data = get_json_data(old_json)
    #print old_json_data
    print '===Added===' 
    #print get_interface_diff(new_json_data,old_json_data)    
    for interface, content in get_diff_list(new_json_data,old_json_data).items():
        print '[[{Interface}]]'.format(Interface=interface)
        print content
    print '===Deleted==='
    #print get_interface_diff(old_json_data,new_json_data)
    for interface, content in get_diff_list(old_json_data,new_json_data).items():
        print '[[{Interface}]]'.format(Interface=interface)
        print content

if __name__ == '__main__':
    main(sys.argv[1:])

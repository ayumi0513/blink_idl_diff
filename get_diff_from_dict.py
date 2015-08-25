import json
import sys

new_json = 'json_dict1.json'
old_json = 'json_dict2.json'


#load a json file into a dictionary
def get_json_data(fname):
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



def compare_data(dic1,dic2,key,output):
    if not dic1[key] == dic2[key]:
        if key == 'FilePath':
            output.append('[{Key}]{FilePath}'.format(Key=key,FilePath=dic1['FilePath']))
        else:
            for key_element in dic1[key]:
                if not key_element in dic2[key]:
                    if key == 'Attribute':
                        output.append('[{Key}]Type:{Type},Name:{Name}'.format(Key=key,Type=key_element['Type'],Name=key_element['Name']))
                    elif key == 'Const':
                        output.append('[{Key}]Type:{Type},Name:{Name},Value:{Value}'.format(Key=key,Type=key_element['Type'],Name=key_element['Name'],Value=key_element['Value']))
                    elif key == 'ExtAttributes':
                        output.append('[{Key}]Name:{Name}'.format(Key=key,Name=key_element['Name']))
                    elif key == 'Operation':
                        output.append('[{Key}]Type:{Type},Name:{Name}'.format(Key=key,Type=key_element['Type'],Name=key_element['Name']))
    return output



def get_diff_list(json_data1,json_data2):
    output = []
    for interface, dic1 in json_data1.items():
        if not interface in json_data2:
            output.append('[[Interface]]Name:{0},Path:{1}'.format(dic1['Name'],dic1['FilePath']))
        else:
            print '[[Interface]]Name:{0},Path:{1}'.format(dic1['Name'],dic1['FilePath'])
            output = compare_data(dic1,json_data2[interface],'Attribute',output)
            output = compare_data(dic1,json_data2[interface],'Const',output)
            output = compare_data(dic1,json_data2[interface],'ExtAttributes',output)
            output = compare_data(dic1,json_data2[interface],'FilePath',output)
            output = compare_data(dic1,json_data2[interface],'Operation',output)
    return output



def main(argv):
    new_json_data = get_json_data(new_json)
    #print new_json_data
    old_json_data = get_json_data(old_json)
    #print old_json_data
    print '===Added===' 
    #print get_interface_diff(new_json_data,old_json_data)    
    for diff in get_diff_list(new_json_data,old_json_data):
        print diff
    print '===Deleted==='
    #print get_interface_diff(old_json_data,new_json_data)
    for diff in get_diff_list(old_json_data,new_json_data):
        print diff

if __name__ == '__main__':
    main(sys.argv[1:])

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



def get_diff_list(json_data1,json_data2):
    output = []
    for interface1, dic1 in json_data1.items():
        if not interface1 in json_data2:
            output.append('[[Interface]]{0},{1}'.format(dic1['Name'],dic1['FilePath']))
        else:
            print '[[Interface]]{0},{1}'.format(dic1['Name'],dic1['FilePath'])
            if not dic1['Attribute'] in json_data2[interface1].values():
                for attr in dic1['Attribute']:
                    if not attr in json_data2[interface1]['Attribute']:
                        output.append('[Attribute]Type:{0},Name:{1}'.format(attr['Type'],attr['Name']))
            if not dic1['Const'] in json_data2[interface1].values():
                for cns in dic1['Const']:
                    if not cns in json_data2[interface1]['Const']:
                        output.append('[Const]Type:{0},Name:{1},Value:{2}'.format(cns['Type'],cns['Name'],cns['Value']))
            if not dic1['ExtAttributes'] in json_data2[interface1].values():
                for ext in dic1['ExtAttributes']:
                    if not ext in json_data2[interface1]['ExtAttributes']:
                        output.append('[ExtAttributes]Name:{0}'.format(ext['Name']))
            if not dic1['FilePath'] in json_data2[interface1].values():
                output.append('[FilePath] : {0}'.format(dic1['FilePath']))
            if not dic1['Operation'] in json_data2[interface1].values():
                for ope in dic1['Operation']:
                    if not ope in json_data2[interface1]['Operation']:
                        output.append('[Operation]Type:{0},Name:{1}'.format(ope['Type'],ope['Name']))
    return output



def main(argv):
    new_json_data = get_json_data(new_json)
    #print new_json_data
    old_json_data = get_json_data(old_json)
    #print old_json_data
    print '===Added Interface===' 
    #print get_interface_diff(new_json_data,old_json_data)    
    for diff in get_diff_list(new_json_data,old_json_data):
        print diff
    print '===Deleted Interface==='
    #print get_interface_diff(old_json_data,new_json_data)
    for diff in get_diff_list(old_json_data,new_json_data):
        print diff

if __name__ == '__main__':
    main(sys.argv[1:])

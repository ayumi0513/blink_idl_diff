import json
import sys

new_json = 'shortA.json'
old_json = 'shortB.json'

#load a json file into a dictionary
def get_json_data(fname):
    f = open(fname,'r')
    json_data = json.load(f)
    #print json.dumps(json_data,sort_keys=True,indent=4)
    f.close()
    return json_data


#make a list of added data
#get_data is 'Attribute' or 'Operation' or 'Const'
def added_data(json_data1,json_data2,get_data):
    output = []
    data1_list = json_data1[get_data]
    data2_list = json_data2[get_data]
    for data1 in data1_list:
        if not data1 in data2_list:
            output.append('{0}(Type:{1},Name:{2}) is added to {3}(Interface:{4})'.format(get_data,data1['Type'],data1['Name'],json_data1['FileName'],json_data1['Name']))
    return output



#make a list of deleted data
#get_data is 'Attribute' or 'Operation' or 'Const'
def deleted_data(json_data1,json_data2,get_data):
    output = [] 
    data1_list = json_data1[get_data]             
    data2_list = json_data2[get_data]
    for data2 in data2_list:
        if not data2 in data1_list:                        
            output.append('{0}(Type:{1},Name:{2}) is deleted from {3}(Interface:{4})'.format(get_data,data2['Type'],data2['Name'],json_data2['FileName'],json_data2['Name']))
    return output


#put all added data in one
def all_added_data(json_data1,json_data2):
    output = []
    if added_data(json_data1,json_data2,'Attribute'):
        for added_attr in added_data(json_data1,json_data2,'Attribute'):
            output.append(added_attr)
    if added_data(json_data1,json_data2,'Operation'):
        for added_ope in added_data(json_data1,json_data2,'Operation'):
            output.append(added_ope)
    if added_data(json_data1,json_data2,'Const'):
        for added_cons in added_data(json_data1,json_data2,'Const'):
            output.append(added_cons)
    return output


#put all deleted data in one
def all_deleted_data(json_data1,json_data2):
    output = []
    if deleted_data(json_data1,json_data2,'Attribute'):
        for deleted_attr in deleted_data(json_data1,json_data2,'Attribute'):
            output.append(deleted_attr)
    if deleted_data(json_data1,json_data2,'Operation'):
        for deleted_ope in deleted_data(json_data1,json_data2,'Operation'):
            output.append(deleted_ope)
    if deleted_data(json_data1,json_data2,'Const'):
        for deleted_cons in deleted_data(json_data1,json_data2,'Const'):
            output.append(deleted_cons)
    return output


def print_all_diff(json_data1,json_data2):
    print ' '
    print '[Added]'
    for data in all_added_data(json_data1,json_data2):
        print data
    print ' '    
    print '[Deleted]'
    for data in all_deleted_data(json_data1,json_data2):
        print data



def main(argv):
    json_data1 = get_json_data(new_json)
    json_data2 = get_json_data(old_json)
    print_all_diff(json_data1,json_data2)

if __name__ == '__main__':
    main(sys.argv[1:])

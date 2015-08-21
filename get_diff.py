import json
import sys

new_json = 'A.json'
old_json = 'B.json'

#load a json file into a dictionary
def get_json_data(fname):
    f = open(fname,'r')
    json_data = json.load(f)
    #print json.dumps(json_data,sort_keys=True,indent=4)
    f.close()
    return json_data

def get_idl_name_list(json_data):
    idl_name_list = []
    for data in json_data:
        idl_name_list.append(data['FileName'])
    return idl_name_list

def get_added_idl(json_data_list1,json_data_list2):
    idl_name_list2 = get_idl_name_list(json_data_list2)
    added_idl = []
    for data1 in json_data_list1:
        if not data1['FileName'] in idl_name_list2:
            added_idl.append('idl file {0} is added '.format(data1['FileName']))
            json_data_list1.remove(data1)
    return [added_idl,json_data_list1]


def get_deleted_idl(json_data_list1,json_data_list2):
    idl_name_list1 = get_idl_name_list(json_data_list1)
    deleted_idl = []
    for data2 in json_data_list2:
        if not data2['FileName'] in idl_name_list1:
            deleted_idl.append('idl file {0} is deleted '.format(data2['FileName']))
            json_data_list2.remove(data2)
    return [deleted_idl,json_data_list2]


def get_same_idl(idl_name,json_data_list2):
    for json_data2 in json_data_list2:
        if idl_name == json_data2['FileName']:
            return json_data2

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
def collect_added_data(json_data1,json_data2):
    output = []
    #for added_idl in get_added_idl(json_data1,json_data2):
        #output.append(added_idl)
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
def collect_deleted_data(json_data1,json_data2):
    output = []
    #for deleted_idl in get_deleted_idl(json_data1,json_data2):
        #output.append(deleted_idl)
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



def all_added_data(added_idl_list,json_data_list1,json_data_list2):
    output = []
    for added_idl in added_idl_list:
        output.append(added_idl)
    print ' '
    print '[Added]'
    for json_data1 in json_data_list1:
        json_data2 = get_same_idl(json_data1['FileName'],json_data_list2)
        for added_data in collect_added_data(json_data1,json_data2):
            output.append(added_data)
    return output

   
def all_deleted_data(deleted_idl_list,json_data_list1,json_data_list2):
    output = []
    for deleted_idl in deleted_idl_list:
        output.append(deleted_idl)
    print ' '
    print '[Deleted]'
    for json_data1 in json_data_list1:
        json_data2 = get_same_idl(json_data1['FileName'],json_data_list2)
        for deleted_data in collect_deleted_data(json_data1,json_data2):
            output.append(deleted_data)
    return output



def main(argv):
    json_data_list1 = get_json_data(new_json)
    json_data_list2 = get_json_data(old_json)
    #print_all_diff(json_data1,json_data2)
    added_idl_list = get_added_idl(json_data_list1,json_data_list2)[0]
    deleted_idl_list = get_deleted_idl(json_data_list1,json_data_list2)[0]
    new_json_data_list1 = get_added_idl(json_data_list1,json_data_list2)[1]
    new_json_data_list2 = get_deleted_idl(json_data_list1,json_data_list2)[1]
    output = []
    #for json_data1 in new_json_data1:
        #json_data2 = get_same_idl(json_data1['FileName'],new_json_data2)
        #print_all_diff(json_data1,json_data2)
        #for data in collect_added_data(json_data1,json_data2):
            #output.append(data)
    #for data in output:
        #print data
    for added_data in all_added_data(added_idl_list,new_json_data_list1,new_json_data_list2):
        print added_data
    for deleted_data in all_deleted_data(deleted_idl_list,new_json_data_list1,new_json_data_list2):
        print deleted_data



if __name__ == '__main__':
    main(sys.argv[1:])

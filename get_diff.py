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

def get_idl_name_list(json_data_list):
    idl_name_list = []
    for data in json_data_list:
        idl_name_list.append(data['FileName'])
    return idl_name_list


def get_added_deleted_idl_list_and_new_json_data_list(json_data_list1,json_data_list2):
    idl_name_list = get_idl_name_list(json_data_list2)
    idl_list = []
    for data1 in json_data_list1:
        if not data1['FileName'] in idl_name_list:
            idl_list.append('[idl file] : {0}'.format(data1['FileName']))
            json_data_list1.remove(data1)
    return (idl_list,json_data_list1)



def get_same_idl(idl_name,json_data_list2):
    for json_data2 in json_data_list2:
        if idl_name == json_data2['FileName']:
            return json_data2


#make a list of added (or deleted) data
#get_data is 'Attribute' or 'Operation' or 'Const'
def get_added_deleted_data(json_data1,json_data2,get_data):
    output = []
    data1_list = json_data1[get_data]
    data2_list = json_data2[get_data]
    for data1 in data1_list:
        if not data1 in data2_list:
            output.append('[{0}] : Type:{1},Name:{2} (idl:{3},Interface:{4})'.format(get_data,data1['Type'],data1['Name'],json_data1['FileName'],json_data1['Name']))
    return output




#put all added (or deleted) data in one
def collect_added_deleted_data(json_data1,json_data2):
    output = []
    #for added_idl in get_added_idl(json_data1,json_data2):
        #output.append(added_idl)
    if get_added_deleted_data(json_data1,json_data2,'Attribute'):
        for attr in get_added_deleted_data(json_data1,json_data2,'Attribute'):
            output.append(attr)
    if get_added_deleted_data(json_data1,json_data2,'Operation'):
        for ope in get_added_deleted_data(json_data1,json_data2,'Operation'):
            output.append(ope)
    if get_added_deleted_data(json_data1,json_data2,'Const'):
        for cons in get_added_deleted_data(json_data1,json_data2,'Const'):
            output.append(cons)
    return output



def all_added_deleted_data(idl_list,json_data_list1,json_data_list2):
    output = []
    for idl in idl_list:
        output.append(idl)
    for json_data1 in json_data_list1:
        json_data2 = get_same_idl(json_data1['FileName'],json_data_list2)
        for data in collect_added_deleted_data(json_data1,json_data2):
            output.append(data)
    return output

def print_all_data(idl_list,json_data_list1,json_data_list2):
    for data in all_added_deleted_data(idl_list,json_data_list1,json_data_list2):
        print data

def main(argv):
    new_json_data_list = get_json_data(new_json)
    old_json_data_list = get_json_data(old_json)
    added_idl_list,updated_new_json_data_list = get_added_deleted_idl_list_and_new_json_data_list(new_json_data_list,old_json_data_list)
    deleted_idl_list,updated_old_json_data_list = get_added_deleted_idl_list_and_new_json_data_list(old_json_data_list,new_json_data_list)
    print ' '
    print '===Added==='
    print_all_data(added_idl_list,updated_new_json_data_list,updated_old_json_data_list)
    print ' '
    print '===Deleted==='
    print_all_data(deleted_idl_list,updated_old_json_data_list,updated_new_json_data_list)


if __name__ == '__main__':
    main(sys.argv[1:])

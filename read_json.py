import sys
import json

json_fname = 'json_file.json'


def get_all_interface_dict(fname):
    all_interface_name = []
    f = open(fname,'r')
    json_data = json.load(f)
    interface_dict_list = json_data.values()
    return interface_dict_list

def get_all_interface_name(interface_dict_list):
    all_interface_name = []
    for interface_dict in interface_dict_list:
        interface_contents = interface_dict.values()[0]
        for interface_content in interface_contents:
            all_interface_name.append(interface_content['Name'])
    return all_interface_name

def print_json(fname):
    f = open(fname,'r')
    json_data = json.load(f)
    print json.dumps(json_data,sort_keys=True,indent=4)
    f.close()


def main(argv):
    #print_json(json_fname)
    interface_dict_list = get_all_interface_dict(json_fname)
    #print json.dumps(interface_dict_list,sort_keys=True,indent=4)
    print get_all_interface_name(interface_dict_list)

if __name__ == '__main__':
    main(sys.argv[1:])

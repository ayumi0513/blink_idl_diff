import json
import sys




def load_json_file(filepath):
    """Load a json file into a dictionary
    Args:
        filepath : A file path of a json file that we want to load
    Return : A dictionary that is loaded from the json file
    """
    with open(filepath,'r') as f:
        return json.load(f)

def remove_same_interface(new_loaded_file_data, old_loaded_file_data):
    """Remove Interface data that are common to the two inputs from them.
        Args :
            new_loaded_file_data : A dictionary consists of new json file data loaded by load_json_file() 
            old_loaded_file_data : A dictionary consists of old json file data loaded by load_json_file() 
        Return :
            new_loaded_file_data : A dictionary that is removed some interface data from the input
            old_loaded_file_data : A dictionary that is removed some interface data from the input
    """
    for interface_name, interface_content in new_loaded_file_data.items():
        if interface_name in old_loaded_file_data.keys():
            if interface_content == old_loaded_file_data[interface_name]:
                del new_loaded_file_data[interface_name]
                del old_loaded_file_data[interface_name]
    return [new_loaded_file_data, old_loaded_file_data]

def remove_name_and_filepath(file_data):
    """Remove "Name" and "FilePath" data
        Arg : A dictionary consist of json file data
        Return : A dictionary removed "Name" and "FilePath" data from the input
    """      
    for interface_content in file_data.values():
        for member_name in interface_content.keys():
            if member_name == 'Name' or member_name == 'FilePath':
                del interface_content[member_name]
    return file_data



def add_annotation(comparison_source_file, comparison_object_source_file, diff_tag):
    """Add annotation ("added" or "deleted") into comparison_source_file.
        Args :
            comparison_source_file : A dictionary that we want to add diff_tag
            comparison_object_source_file : A dictionary to compare with comparison_source_file
            diff_tag : An annotation ("added" or "deleted")
        Return :
            A dictionary added diff_tag
    """
    extattributes_and_members = ['ExtAttributes', 'Const', 'Attribute', 'Operation']
    for interface_name, interface_content in comparison_source_file.items():
        if not interface_name in comparison_object_source_file.keys():
            comparison_source_file[interface_name]['diff_tag'] = diff_tag
            for extattributes_or_member in extattributes_and_members:
                for extattributes_or_member_content in interface_content[extattributes_or_member]:
                    extattributes_or_member_content['diff_tag'] = diff_tag
        else:
            for extattributes_or_member in extattributes_and_members:
                for extattributes_or_member_content in interface_content[extattributes_or_member]:
                    if not extattributes_or_member_content in comparison_object_source_file[interface_name][extattributes_or_member]:
                        extattributes_or_member_content['diff_tag'] = diff_tag
    return comparison_source_file



def make_added_and_deleted_diff(new_loaded_file_data, old_loaded_file_data):
    """Make two dictionary(One is added annotations 'added', the other is added anntaitons 'deleted').  
        Args : 
            new_loaded_file_data : A dictionary consists of new json file data loaded by load_json_file() 
            old_loaded_file_data : A dictionary consists of old json file data loaded by load_json_file() 
        Return : 
            added_diff : A dictionary added anntations, 'added'
            deleted_diff : A dictionary added annotations, 'deleted'
    """
    removed_file_data = remove_same_interface(new_loaded_file_data, old_loaded_file_data)
    new_loaded_file_data = removed_file_data[0]
    old_loaded_file_data = removed_file_data[1]
    new_loaded_file_data = remove_name_and_filepath(new_loaded_file_data)
    old_loaded_file_data = remove_name_and_filepath(old_loaded_file_data)
    added_diff = add_annotation(new_loaded_file_data, old_loaded_file_data, 'added')
    deleted_diff = add_annotation(old_loaded_file_data, new_loaded_file_data, 'deleted')
    return [added_diff, deleted_diff]
    

def merge_diff(added_diff, deleted_diff):
    """Merge added_diff into deleted_diff.
        Args : 
            added_diff : A dictionary added annotations, 'added'
            deleted_diff : A dictionary added annotations, 'deleted'
        Return :
            A dictionary merged
    """
    diff = {}
    extattribute_and_members = ['ExtAttributes', 'Const', 'Attribute', 'Operation']
    diff = deleted_diff
    for interface_name, interface_content in added_diff.items():
        if 'diff_tag' in interface_content.keys():
            diff[interface_name] = interface_content
        else:
            for extattribute_or_member in extattribute_and_members:
                for extattributes_or_member_content in interface_content[extattribute_or_member]:
                    if 'diff_tag' in extattributes_or_member_content.keys():
                        diff[interface_name][extattribute_or_member].append(extattributes_or_member_content)
    return diff


def make_json_file(diff_data, filepath):
    """Make a json file consists of diff dictionary.
        Args :
            diff_data : A dictionary that expresses the diff
            filepath: A file path that we want to make
    """
    with open(filepath, 'w') as f:
        json.dump(diff_data, f, indent=4)
        f.close


def main(argv):
    new_json_file = argv[0]
    old_json_file = argv[1]
    new_loaded_file_data = load_json_file(new_json_file)
    old_loaded_file_data = load_json_file(old_json_file)
    added_and_deleted_diff = make_added_and_deleted_diff(new_loaded_file_data, old_loaded_file_data)
    added_diff = added_and_deleted_diff[0]
    deleted_diff = added_and_deleted_diff[1]
    merged_diff = merge_diff(added_diff, deleted_diff)
    make_json_file(merged_diff, 'merged.json')

if __name__ == '__main__':
    main(sys.argv[1:])

import os, sys

argvs = sys.argv
argc = len(argvs)

#print argvs,argc

def find_all_files(directory):
    for root, dirs, files in os.walk(directory):
        yield root
        for file in files:
            yield os.path.join(root, file)

def find_idl_files(dir_name):
	file_list = []
	for file in find_all_files(dir_name):
		if file.endswith('.idl'):
    			file_list.append(file)
	return file_list


if __name__ == '__main__':
	dir_name = argvs[1]
	print find_idl_files(dir_name)
	print 'the number of idl files is' , len(find_idl_files(dir_name))

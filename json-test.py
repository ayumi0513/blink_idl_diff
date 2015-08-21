import json

def jsoncx():
    json_data = {'PYTHON':'python','JSON':('json','json?')}
    return json.dumps(json_data,indent = 4)

def main():
    print jsoncx()

if __name__ == '__main__':
    main()



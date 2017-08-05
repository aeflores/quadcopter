import json
import sys

def main():
        f = open(sys.argv[1], 'r')
        for line in f:
            json_data = json.loads(line)
            print json_data[sys.argv[2]]
        f.close()
	
main()

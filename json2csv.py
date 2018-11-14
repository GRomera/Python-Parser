#import pip
try:
    import yaml
    #__import__("PyYAML")
except ImportError:
    import pip
    pip.main(["install", "PyYAML"])
    import yaml

import sys
import csv
import json
#import yaml

DEFAULT_NULL_DATA = "N/A"

# read target files from command line
jsonName = sys.argv[1]# input("JSON File: ")
csvName = sys.argv[2]# input("CSV File: ")
filterName = sys.argv[3]

# this is where we the data from the JSON before we write it to the CSV
#fieldnames = set([])
fieldnames = []
dataFilter = {}

def FilterData(d1, d2, lastKey = None):
    if (isinstance(d1, list) and isinstance(d2, list)) and (lastKey is not None):
        arr = []
        for elem in d1:
            arr.append(FilterData(elem, d2[0], lastKey))
        return arr

    elif isinstance(d1, dict) and isinstance(d2, dict):
        filteredData = {}
        for k in d2.keys():
            if k in d1.keys():
                filteredData[k] = FilterData(d1[k], d2[k], k)
        return filteredData

    else:
        return d1
# flatten out supplied dictionary structure
def ProcessElement(element, data=[], keyName="", indentLevel=0):

    global lastAddedRow
    global lastIndentLevel

    if isinstance(element, list):
        #print("LIST")
        index = 1
        for e in element:
            ProcessElement(e, data, keyName, indentLevel+1)# + "[" + str(index) + "]")
            

            index = index + 1

    elif isinstance(element, dict):
        #print("DICT")
        for k in element.keys():
            ProcessElement(element[k], data, keyName + "_" + k, indentLevel) #TODO look at using RegEx to get rid of initial _ (or use level > 0)

    else:
        if keyName not in fieldnames:
            fieldnames.append(keyName)

        #data.append({name: element})

        if len(data) == 0:
            data.append({keyName: element})
            lastAddedRow = 0
            lastIndentLevel = 0
        else:

            if keyName not in data[lastAddedRow].keys():
                (data[lastAddedRow])[keyName] = element #add new row
            else:
                data.append({keyName: element})
                lastAddedRow += 1

    return data


with open(jsonName, "r") as json_file:
    json_data = json.load(json_file)

    with open(filterName, "r") as f:
        dataFilter = yaml.safe_load(f)
        #print(dataFilter)
        json_data = FilterData(json_data, dataFilter)
        #print(json.dumps(json_data, indent=4, sort_keys=True))

    processed_data = ProcessElement(json_data)

    with open(csvName, "w") as csvFile:
        #CsvWriter = csv.DictWriter(csvFile, fieldnames = fieldnames)
        CsvWriter = csv.DictWriter(csvFile, delimiter=',', lineterminator='\n', fieldnames=fieldnames) #Omid's Code

        CsvWriter.writeheader()
        CsvWriter.writerows(processed_data)

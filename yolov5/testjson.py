import json

# Open the JSON file for reading
with open('labels.json', 'r') as f:

    # Load the contents of the file into a dictionary
    labelsJson = json.load(f, strict=False)

    # Print the contents of the dictionary
    print(labelsJson)

    runOutput = "test"
    inferenceJson = {
                        'runOutput': runOutput,
                        'labels': labelsJson
                    }
    infString = json.dumps(inferenceJson, indent=4)
    print (infString)



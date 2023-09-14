#!/bin/bash

function profiling_func() {
    local stepno="$1"
    local description="$2"
    local data="$3"

    local timestamp=$(date -u +'%Y-%m-%dT%H:%M:%SZ')

    if [ -z "$(echo "$data" | jq '.stepsProfile')" ]; then
        data=$(echo "$data" | jq '.stepsProfile = []')
    fi
    
    # Construct the step object
    local step_object="{\"step$stepno\": {\"description\": \"$description\", \"timestamp\": \"$timestamp\"}}"
    
    # Add the step object to 'stepsProfile' array
    updated_data=$(echo "$data" | jq --argjson step "$step_object" '.stepsProfile += [$step]')
    #write to file
    echo "$updated_data" -> profiling.json
    
    echo "$updated_data"
}
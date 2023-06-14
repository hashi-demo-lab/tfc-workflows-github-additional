# get workspace outputs
import os
import requests
import json
import logging

def get_workspace_outputs(workspace_id):
    outputs_endpoint = f"https://app.terraform.io/api/v2/workspaces/{workspace_id}/current-state-version-outputs"
    try:
        response = requests.get(outputs_endpoint, headers=headers)
        response.raise_for_status() # raise an exception if response status code is not 200 OK
        outputs = response.json()
        return outputs
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve workspace outputs. Error: {e}")
        return None     


# Set your Terraform Cloud API token
api_token = os.getenv('TF_API_TOKEN')
workspace_id = os.getenv('WORKSPACE_ID')

headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/vnd.api+json",
}

# Retrieve workspace outputs as JSON
outputs = get_workspace_outputs(workspace_id)
if outputs:
    json_text = json.dumps(outputs)
    print(json_text)
else:
    print("Failed to retrieve workspace outputs.")
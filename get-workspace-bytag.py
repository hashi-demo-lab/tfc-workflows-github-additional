# get workspace outputs
import os
import requests
import json
import logging

def get_workspaces_by_tag(api_token, organization, querystring):
    workspaces_endpoint = f"https://app.terraform.io/api/v2/organizations/{organization}/workspaces"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/vnd.api+json",
    }

    try:
        response = requests.get(workspaces_endpoint, headers=headers, params=querystring)
        response.raise_for_status()
        outputs = response.json()
        return outputs

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve workspaces. Error: {e}")
        return None

# Set your Terraform Cloud API token
api_token = os.getenv('TF_API_TOKEN')
organization = os.getenv('TF_CLOUD_ORGANIZATION')
querystring = {"fields[workspace][]=assessments_enabled&search[tags]":"f5","sort":"name"}

headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/vnd.api+json",
}

# Retrieve workspace outputs as JSON
outputs = get_workspaces_by_tag(api_token, organization, querystring)
if outputs:
    json_text = json.dumps(outputs)
    print(json_text)
else:
    print("Failed to retrieve workspace outputs.")
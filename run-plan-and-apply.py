import os
import requests
import json
import logging

def create_terraform_run(workspace_id, api_token):
    endpoint = "https://app.terraform.io/api/v2/runs"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/vnd.api+json",
    }
    payload = {
        "data": {
            "attributes": {
                "is-destroy": False,
                "refresh": True,
                "refresh-only": False,
                "allow-config-generation": True
            },
            "relationships": {
                "workspace": {
                    "data": {
                        "type": "workspaces",
                        "id": workspace_id
                    }
                }
            },
            "type": "runs"
        }
    }

    try:
        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()  # raise an exception if response status code is not 200 OK
        run_data = response.json()
        return run_data
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to create Terraform run. Error: {e}")
        return None

# Set your Terraform Cloud API token and workspace ID
api_token = os.getenv('TF_API_TOKEN')
workspace_id = os.getenv('WORKSPACE_ID')

# Create a Terraform run
run_data = create_terraform_run(workspace_id, api_token)
if run_data:
    json_text = json.dumps(run_data)
    print(json_text)
else:
    print("Failed to create Terraform run.")

# tfc-workflows-github-addon


## Example usage from github actions

``` yaml
env:
  # No need to pass as inputs to each action
  TF_CLOUD_ORGANIZATION: ${{ vars.TF_CLOUD_ORGANIZATION }}
  TF_API_TOKEN: ${{ secrets.TF_API_TOKEN }}
  TF_WORKSPACE: ${{ vars.TF_WORKSPACE }}
  TF_DIRECTORY: "./terraform"

jobs:
  terraform-api-driven:
    runs-on: "ubuntu-latest"
    steps:
      - uses: actions/checkout@v3
      - name: Upload configuration version
        uses: hashicorp/tfc-workflows-github/actions/upload-configuration@v1.0.1
        id: upload
        with:
          workspace: ${{ env.TF_WORKSPACE }}
          directory: ${{ env.TF_DIRECTORY }}
          
      - name: Run Terraform Plan
        uses: hashicorp/tfc-workflows-github/actions/create-run@v1.0.1
        continue-on-error: true
        id: run-plan
        with:
          workspace: ${{ env.TF_WORKSPACE }}
          configuration_version: ${{ steps.upload.outputs.configuration_version_id }}
      - name: Log Error
        if: ${{ steps.run-plan.outputs.plan_status != 'finished' }} 
        run: |
          echo "An error occurred in the previous step."
          echo "The error message was: ${{ steps.run-plan.outcome }}"
          echo "run_status: ${{ steps.run-plan.outputs.run_status }}"

          
      - name: Discard Terraform Run
        if: ${{ steps.run-plan.outputs.plan_status != 'finished' }} 
        uses: hashicorp/tfc-workflows-github/actions/discard-run@v1.0.1
        id: discard-run
        with:
          run: ${{ steps.run-plan.outputs.run_id }}
          comment: "Run discarded due to error ${{ steps.run-plan.outputs.plan_status }}"

      - name: Catch Error   
        if: ${{ steps.run-plan.outputs.plan_status != 'finished' }} 
        run: | 
          exit 1

      - uses: hashicorp/tfc-workflows-github/actions/plan-output@v1.0.1
        name: Get plan output
        id: plan-output
        with:
          plan: ${{ steps.run-plan.outputs.plan_id }}
        
      - name: Reference plan output
        run: |
          echo "Plan status: ${{ steps.plan-output.outputs.plan_status }}"
          echo "Resources to Add: ${{ steps.plan-output.outputs.add }}"
          echo "Resources to Change: ${{ steps.plan-output.outputs.change }}"
          echo "Resources to Destroy: ${{ steps.plan-output.outputs.destroy }}"
          echo 'plan_payload: ${{ steps.run-plan.outputs.payload }}'
    
      - name: Get workspace id - jq
        id: workspace_id
        run: |
          echo '${{ steps.run-plan.outputs.payload }}' > payload.json
          echo "workspace_id=$(jq -r '.included[] | select(.type == "workspaces") | .id' < payload.json)" >> $GITHUB_OUTPUT
      - name: Checkout addons
        uses: actions/checkout@v3
        with:
          ref: main
          repository: hashi-demo-lab/tfc-workflows-github-addon
          path: addon
      - name: Setup Python
        uses: actions/setup-python@v4.6.0
        with:
          python-version: '3.10'
          cache: 'pip'
      - name: install-python-dep
        run: pip install -r ./addon/requirements.txt
      - name: get-workspace-outputs
        id: get-ws-outputs
        run: |
          PYTHON_OUT=$(python ./addon/get-workspace-outputs.py)
          echo "python_output=$PYTHON_OUT" >> $GITHUB_OUTPUT
        env:
          WORKSPACE_ID: ${{ steps.workspace_id.outputs.workspace_id }}
      - name: set_output
        id: set_output
        run: |
          echo "Python output: ${{ steps.get-ws-outputs.outputs.python_output }}"
          export WORKSPACE_OUTPUTS=$(echo '${{ steps.get-ws-outputs.outputs.python_output }}' | jq -r '[.data[] | {name: .attributes.name, value: .attributes.value}] | tojson')
          echo "workspace_outputs=$WORKSPACE_OUTPUTS" >> $GITHUB_OUTPUT
    outputs: 
      workspace_outputs: ${{ steps.set_output.outputs.workspace_outputs }}
# traffic_discovery_status_report
Traffic Discovery Status Report retrieves and filters traffic discovery status for all HALO groups. the script exports results into external CSV file format.

## Filters:
the script supports 2 types of filters that can be used to filter out the resutls:
- Filter results based on traffic discovery status
   - **ENABLED** get all HALO groups with TD status enabled/true
   - **DISABLED** get all HALO groups with TD status disabled/false
   - **ALL** [default] get all HALO groups with both TD status enabled and disabled
- Filter results based on HALO group id
   - **ALL** [default] get TD status for all HALO groups in the provided account
   - **GROUP_ID** get TD status for the provided HALO group ID and all it's first level sub-groups.

## Requirements:
- CloudPassage Halo API key (with Auditor privileges).
- Python 3.6 or later including packages specified in "requirements.txt".

## Installation:
```
   git clone https://github.com/cloudpassage/traffic_discovery_status_report.git
   cd traffic_discovery_status_report
   pip install -r requirements.txt
```

## Configuration:
| Variable | Description | Default Value |
| -------- | ----- | ----- |
| HALO_API_KEY | ID of HALO API Key | ef\*\*ds\*\*fa |
| HALO_API_SECRET_KEY | Secret of HALO API Key | fgfg\*\*\*\*\*heyw\*\*\*\*ter352\*\*\* |
| HALO_API_HOSTNAME | Halo API Host Name | https://api.cloudpassage.com |
| HALO_API_PORT | Halo API Port Number | 443 |
| HALO_API_VERSION | HALO EndPoint Version | v1 |
| OUTPUT_DIRECTORY | Location for generated CSV file | /tmp |

## How the scripts works:
- Checking and validation of the provided configuration parameters and fails in case of missing any required parameter.
- Use HALO API key id/secret to generate access token to be used to access Protected HALO API resources.
- Retrieving the list of HALO Groups. (Script provides ability to grap all groups, all first level childs of a specific group, a specific group)
- For every every group retrieved from the previous call, the script retrieves the traffic discovery status and group name.
- Formating and exporting all retreived report data of into CSV file format and save it in the provided output directory.

## How to run the tool (stand-alone):
To run the script follow the below steps.
1.  Navigate to the script root directory that contains the python module named "app.py", and run it as described below;
```
    cd traffic_discovery_status_report
    python app.py
    Enter Traffic Discovery (TD) Status 'ENABLED / DISABLED / ALL (Default)': 
    Enter Group ID 'ALL (Default)': 
```

## How to run the tool (containerized):
- Clone the script repository:
```
   git clone https://github.com/cloudpassage/traffic_discovery_status_report.git
```

- Build the docker image:
```
   cd traffic_discovery_status_report
   docker build -t traffic_discovery_status_report .
```

- Run the docker container:
```
    docker run -it \
    -e HALO_API_KEY=$HALO_API_KEY \
    -e HALO_API_SECRET_KEY=$HALO_API_SECRET_KEY \
    -e HALO_API_HOSTNAME=$HALO_API_HOSTNAME \
    -v $OUTPUT_DIRECTORY:/tmp \
    traffic_discovery_status_report
```
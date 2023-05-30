# custom_sva_scan_results_report
Custom SVA Scan Results Report shows all software vulnerabilities for each server included in the provided HALO group scope. the script exports results into external CSV file format.

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
| HALO_GROUP_ID | Halo Group ID | 0962\*\*\*\*013\*\*\*ec22\*\*\* |

## How the scripts works:
- Checking and validation of the provided configuration parameters and fails in case of missing any required parameter.
- Use HALO API key id/secret to generate access token to be used to access Protected HALO API resources.
- Retrieving the list of servers that belongs the provided HALO group/groups.
- For every server retrieved from the previous call, the script retrieves list of all results (vulnerable software packages and non-vulnerable packages) detected by the most recent vulnerability scan on that server.
- For each vulnerable package, all of its known vulnerabilities (CVEs) are listed also.
- Formating and exporting all retreived Report data of into CSV file format and save it in the provided output directory.

## How to run the tool (stand-alone):
To run the script follow the below steps.
1.  Navigate to the script root directory that contains the python module named "app.py", and run it as described below;
```
    cd traffic_discovery_status_report
    python app.py
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
    -e HALO_GROUP_ID=$HALO_GROUP_ID \
    -v $OUTPUT_DIRECTORY:/tmp \
    traffic_discovery_status_report
```
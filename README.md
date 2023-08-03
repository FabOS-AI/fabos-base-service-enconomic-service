# fabos-wbd

AAS Server REST API can be found here: https://app.swaggerhub.com/apis/BaSyx/basyx_asset_administration_shell_repository_http_rest_api/v1
Start AAS Server: https://wiki.eclipse.org/BaSyx_/_Documentation_/_Components_/_AAS_Server 

AAS Server:
http://localhost:8081/aasServer/shells/

## Setup

- Start AAS Server
- Start WBD service
- Start Frontend (https://github.com/FabOS-AI/fabos-base-service-enconomic-service-frontend)

## Start

```
# Start server - sometimes docker has to be stopped, removed and started again
# docker run --name=aas -p 8081:4001 eclipsebasyx/aas-server:0.1.1-PREVIEW

# run docker - in C:/user there need to be two config files "aas.properties" and "context.properties" (copies are found in this project)
docker run --name=aas -p 8081:4001 -v C:/user:/usr/share/config eclipsebasyx/aas-server:1.3.0

# start the WBD server
# AAS Example data for machine and service representation is stored in "WBDService.json" and can be manually edited or with an AAS Editor
py server.py

# After starting the server, start the frontend (see frontend description - https://github.com/FabOS-AI/fabos-base-service-enconomic-service-frontend)
# For changing to a different address/port change adress in "client-config.yaml", "server-config.yaml" and "context.properties"
```

## Create Training data
```

# run both scripts in order to create training data for the machine and the service clustering
# change the files for variable data size 100/1000/100000 ...

py maschine_training_data.py
py service_training_data.py

```

## Clustering
```

# run script to save maschine and service cluster results used to calculate economical factor means 
# change file to read in the correct training data file (i.e. 100/1000/10000 ...)
# predictions_maschine.csv and predictions_service.csv will be generated with the clustering results for later use

py clustering.py

```
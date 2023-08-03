import requests
from pathlib import Path
import json
import copy
import xml.etree.ElementTree as ET

class AASClient:
    def __init__(self, host):
        self.host = host

        #create AAS and  submodels with JSON
        self.aas_file = json.load(open(Path(__file__).parent.joinpath("aas_data", "WBDService.json") ))
        self.aas = self.aas_file["assetAdministrationShells"][0]

        #set aas and submodel id
        self.aas_id = self.aas["identification"]["id"]
        self.submodel_id = []

    def get_all(self):
        r = requests.get(f"{self.host}/")
        print(f"{self.host}/")
        if r.status_code != 200:
            raise RuntimeError(f"request failed. {r}")
        return r.json()

    def create_aas(self):
        r = requests.put(f"{self.host}//{self.aas_id}/", json=self.aas)
        headers = {'Content-Type': 'application/xml'}
        print("Posting aas: " + self.aas_id)
        print(f"{self.host}/{self.aas_id}")
        if r.status_code != 200:
            raise RuntimeError(f"request failed. {r}")

    def create_submodel(self, websocketEndpoint):
        submodels = copy.deepcopy(self.aas_file["submodels"])
        for i, model in enumerate(submodels):
            self.submodel_id.extend({model["idShort"]})
            print("Posting Submodel: " + self.submodel_id[i])
            print(f"{self.host}//{self.aas_id}/aas/submodels/{self.submodel_id[i]}/")

            r = requests.put(f"{self.host}//{self.aas_id}/aas/submodels/{self.submodel_id[i]}/", json=submodels[i])
            if r.status_code != 200:
                raise RuntimeError(f"request failed. {r}")
    
    def get_aas(self):
        #print(f"{self.host}//{self.aas_id}/aas/submodels/{self.submodel_id}/submodel/values/")
        r = requests.get(f"{self.host}//{self.aas_id}/")
        print(r)
        if r.status_code != 200:
            raise RuntimeError(f"request failed. {r}")
        return r.json()
    
    def get_submodels(self):
        #print(f"{self.host}//{self.aas_id}/aas/submodels/{self.submodel_id}/submodel/values/")
        r = requests.get(f"{self.host}//{self.aas_id}/aas/submodels/")
        print(r)
        if r.status_code != 200:
            raise RuntimeError(f"request failed. {r}")
        return r.json()
    
    def get_maschine_submodel(self):
        #print(f"{self.host}//{self.aas_id}/aas/submodels/{self.submodel_id}/submodel/values/")
        r = requests.get(f"{self.host}//{self.aas_id}/aas/submodels/WBDMaschineSubmodel/submodel")
        print(r)
        if r.status_code != 200:
            raise RuntimeError(f"request failed. {r}")
        return r.json()
    
    def get_ai_submodel(self):
        #print(f"{self.host}//{self.aas_id}/aas/submodels/{self.submodel_id}/submodel/values/")
        r = requests.get(f"{self.host}//{self.aas_id}/aas/submodels/WBDAISubmodel/submodel")
        print(r)
        if r.status_code != 200:
            raise RuntimeError(f"request failed. {r}")
        return r.json()
    
    def get_maschine_user_submodel(self):
        #print(f"{self.host}//{self.aas_id}/aas/submodels/{self.submodel_id}/submodel/values/")
        r = requests.get(f"{self.host}//{self.aas_id}/aas/submodels/WBDMaschineUserSubmodel/submodel")
        print(r)
        if r.status_code != 200:
            raise RuntimeError(f"request failed. {r}")
        return r.json()
    
    def set_value(self, submodelId, elementId, value):
        r = requests.put(f"{self.host}//{self.aas_id}/aas/submodels/{submodelId}/submodel/submodelElements/{elementId}/value",value)
        print(r)
        if r.status_code != 200:
            raise RuntimeError(f"request failed. {r}")
        try:
            # Try to parse the response as JSON
            json_response = r.json()
            return json_response
        except ValueError:
            # If the response cannot be parsed as JSON, return the raw response content
            return r.content
        #return r.json()
        
    
    #http://localhost:8081/aasServer/shells/AssetAdministrationShell---6B851AE4/aas/submodels
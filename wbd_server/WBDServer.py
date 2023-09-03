import asyncio
import websockets
import yaml
from aas_client.AASClient import AASClient
from omegaconf import OmegaConf
from pprint import pprint
from wbd_calculation.WBDCalc_withAAS import CostsMaschineBase
from wbd_calculation.WBDCalc_withAAS import CostsAI
import pandas as pd
import numpy as np

costsBase = CostsMaschineBase()
costsAI = CostsAI()


class WBDServer:
    
    def __init__(self):
        self.config = OmegaConf.load("server-config.yaml")

        # create AAS from JSON files
        self.aas_client = AASClient(self.config["aas"]["host"])
        self.aas_client.get_all()
        self.aas_client.create_aas()
        self.aas_client.create_submodel(websocketEndpoint=self.config.aas.publish_endpoint)
        values = self.aas_client.get_aas()
        self.selected_machine = ""
        self.selected_service = ""
        # print("values stores in AAS server:", values)

    async def ws_handler(self, websocket, path):

        while True:
            order = await websocket.recv()
            print(f"incoming order: {order}")

            if (order == "calc"):
                print(f"calc request WS")
                costsBase.init_submodel()
                costsAI.init_submodel()
                costsBase.calc()
                costsAI.calc()
                await websocket.send("result")
                # costsAI.calc()
                await asyncio.sleep(1) # needed for unknown reasons - (MUST be 0)

            if ("combi" in order):
                print(f"combi request WS")
                parts = order.split(";")
                self.selected_machine = parts[1]
                self.selected_service = parts[2]

                # update the AAS with the factor values of the trained model
                pd_machines = pd.read_csv('example_maschines.csv', header=0)
                pd_services = pd.read_csv('example_services.csv', header=0)
                machine_prediction = pd_machines.loc[(pd_machines["Name"] == self.selected_machine)]['prediction'].values[0]
                service_prediction = pd_services.loc[(pd_services["Name"] == self.selected_service)]['prediction'].values[0]

                pd_combi = pd.read_csv('means_clustering_10000.csv', header=0)

                #print(pd_combi.loc[(pd_combi["Cluster_Maschine"] == machine_prediction) ])

                AbsatzmengeFaktor = pd_combi.loc[((pd_combi["Cluster_Maschine"] == machine_prediction) & (pd_combi["Cluster_Service"] == service_prediction))]['AbsatzmengeFaktor_mean'].values[0]
                PersonalkostenFaktor = pd_combi.loc[((pd_combi["Cluster_Maschine"] == machine_prediction) & (pd_combi["Cluster_Service"] == service_prediction))]['PersonalkostenFaktor_mean'].values[0]
                EnergiekostenFaktor = pd_combi.loc[((pd_combi["Cluster_Maschine"] == machine_prediction) & (pd_combi["Cluster_Service"] == service_prediction))]['EnergiekostenFaktor_mean'].values[0]
                ReparaturkostenProStueckFaktor = pd_combi.loc[((pd_combi["Cluster_Maschine"] == machine_prediction) & (pd_combi["Cluster_Service"] == service_prediction))]['ReparaturkostenProStueckFaktor_mean'].values[0]
                MaterialkostenFaktor = pd_combi.loc[((pd_combi["Cluster_Maschine"] == machine_prediction) & (pd_combi["Cluster_Service"] == service_prediction))]['MaterialkostenFaktor_mean'].values[0]
                WartungskostenFaktor = pd_combi.loc[((pd_combi["Cluster_Maschine"] == machine_prediction) & (pd_combi["Cluster_Service"] == service_prediction))]['WartungskostenFaktor_mean'].values[0]
                AbsatzpreisFaktor = pd_combi.loc[((pd_combi["Cluster_Maschine"] == machine_prediction) & (pd_combi["Cluster_Service"] == service_prediction))]['AbsatzpreisFaktor_mean'].values[0]
            
                # send values to aas server
                self.aas_client.set_value("WBDAISubmodel", "AbsatzmengeFaktor", str(AbsatzmengeFaktor))
                self.aas_client.set_value("WBDAISubmodel", "PersonalkostenFaktor", str(PersonalkostenFaktor))
                self.aas_client.set_value("WBDAISubmodel", "EnergiekostenFaktor", str(EnergiekostenFaktor))
                self.aas_client.set_value("WBDAISubmodel", "ReparaturkostenProStueckFaktor", str(ReparaturkostenProStueckFaktor))
                self.aas_client.set_value("WBDAISubmodel", "MaterialkostenFaktor", str(MaterialkostenFaktor))
                self.aas_client.set_value("WBDAISubmodel", "WartungskostenFaktor", str(WartungskostenFaktor))
                self.aas_client.set_value("WBDAISubmodel", "AbsatzpreisFaktor", str(AbsatzpreisFaktor))

                await websocket.send("selected")
                # costsAI.calc()
                await asyncio.sleep(1) # needed for unknown reasons - (MUST be 0)


    def run_server(self):
        start_server = websockets.serve(self.ws_handler, **self.config["websocket"])

        asyncio.get_event_loop().run_until_complete(start_server)
        print("waiting ...")
        asyncio.get_event_loop().run_forever()

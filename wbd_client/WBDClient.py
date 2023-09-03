from aas_client.AASClient import AASClient
import asyncio
import websockets
from omegaconf import OmegaConf
import numpy as np

class WBDClient:
    def __init__(self):
        self.config = OmegaConf.load("client-config.yaml")
        aas_client = AASClient(self.config["aas"]["host"])
        values = aas_client.get_values()
        self.uri = values["MyProperty"]
        print(f"uri: {self.uri}")

    def receive(self):
        asyncio.get_event_loop().run_until_complete(self.ws_client())

    async def ws_client(self):
        async with websockets.connect(self.uri) as websocket:
            name = "WBDClient_websocket"

            await websocket.send(name)
            print(f"> {name}")
            
            i = 0
            while True:
                response = await websocket.recv()
                print(response)
                if isinstance(response, bytes):
                    data = np.frombuffer(response, dtype=np.int16)

                    print(f"{i}, size={len(response)}, max={np.max(np.abs(data))}")
                i += 1

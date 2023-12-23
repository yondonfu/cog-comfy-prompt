import subprocess
import threading
import time
from cog import BasePredictor, Input, Path, File
import uuid
import json
import urllib
import websocket
from PIL import Image
from urllib.error import URLError
from urllib.parse import urlparse
import pathlib
import os
import shutil
from typing import List


class Predictor(BasePredictor):
    def setup(self):
        self.server_address = "127.0.0.1:8188"
        self.start_server()

    def start_server(self):
        server_thread = threading.Thread(target=self.run_server)
        server_thread.start()

        while not self.is_server_running():
            time.sleep(1)

        print("Server is up and running!")

    def run_server(self):
        command = "python ComfyUI/main.py --extra-model-paths-config extra_model_paths.yaml"
        server_process = subprocess.Popen(command, shell=True)
        server_process.wait()

    # hacky solution, will fix later
    def is_server_running(self):
        try:
            with urllib.request.urlopen("http://{}/history/{}".format(self.server_address, "123")) as response:
                return response.status == 200
        except URLError:
            return False

    def queue_prompt(self, prompt, client_id):
        p = {"prompt": prompt, "client_id": client_id}
        data = json.dumps(p).encode('utf-8')
        req = urllib.request.Request(
            "http://{}/prompt".format(self.server_address), data=data)
        return json.loads(urllib.request.urlopen(req).read())

    def get_outputs(self, ws, prompt, client_id):
        prompt_id = self.queue_prompt(prompt, client_id)['prompt_id']
        outputs = {}
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break  # Execution is done
            else:
                continue  # previews are binary data

        history = self.get_history(prompt_id)[prompt_id]
        for o in history['outputs']:
            for node_id in history['outputs']:
                node_output = history['outputs'][node_id]
                print("node output: ", node_output)

                if 'images' in node_output:
                    images_output = []
                    for image in node_output['images']:
                        images_output.append(image['filename'])

                    outputs[node_id] = images_output

                if 'gifs' in node_output:
                    gifs_output = []
                    for gif in node_output['gifs']:
                        gifs_output.append(gif['filename'])

                    outputs[node_id] = gifs_output

        return outputs

    def get_history(self, prompt_id):
        with urllib.request.urlopen("http://{}/history/{}".format(self.server_address, prompt_id)) as response:
            return json.loads(response.read())

    def predict(
        self,
        prompt_file: File = Input(
            description="File with ComfyUI API prompt in JSON format"),
        input_files: List[File] = Input(
            description="Input files for ComfyUI prompt",
            default=[]
        )
    ) -> Path:
        input_dir = "ComfyUI/input"
        output_dir = "ComfyUI/output"

        if os.path.exists(input_dir):
            shutil.rmtree(input_dir)
        os.makedirs(input_dir)

        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)

        for file in input_files:
            fname = Path(urlparse(file.url).path).name
            input_path = f"{input_dir}/{fname}"
            with open(input_path, "wb") as f:
                f.write(file.read())

        prompt = json.loads(prompt_file.read())
        img_output_path = self.get_prompt_output(
            prompt=prompt,
        )
        return img_output_path

    def get_prompt_output(self, prompt) -> Path:
        client_id = str(uuid.uuid4())
        ws = websocket.WebSocket()
        ws.connect(
            "ws://{}/ws?clientId={}".format(self.server_address, client_id))
        outputs = self.get_outputs(ws, prompt, client_id)

        for node_id in outputs:
            for output_data in outputs[node_id]:
                output_path = f"ComfyUI/output/{output_data}"
                # Return the first output found for now
                # TODO: Support multiple outputs
                return Path(output_path)

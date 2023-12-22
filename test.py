import json
import tempfile
import requests
import os
from pathlib import Path
import urllib

if __name__ == "__main__":
  fname = "prompts/text-to-image-sdxl-turbo.json"
  with open(fname, "r") as f:
    prompt = json.load(f)

  prompt["20"]["inputs"]["ckpt_name"] = "sd_xl_turbo_1.0_fp16.safetensors"
  prompt["5"]["inputs"]["width"] = 1024
  prompt["5"]["inputs"]["height"] = 576
  prompt["6"]["inputs"]["text"] = "A cat meditating in front of a temple, anime"

  tmp_prompt_file = tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".json", dir="files")
  json.dump(prompt, tmp_prompt_file)
  tmp_prompt_file.close()

  file_server_url = "http://127.0.0.1:8000"
  prompt_file_url = f"{file_server_url}/file/{Path(tmp_prompt_file.name).name}"

  data = {
    "input": {
      "prompt_file": prompt_file_url
    },
    "output_file_prefix": file_server_url + "/file/"
  }

  url = "http://localhost:5000/predictions"
  result = requests.post(url, json=data)
  print(result.json())

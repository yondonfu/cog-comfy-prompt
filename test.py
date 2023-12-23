import json
import tempfile
import requests
import os
from pathlib import Path
import urllib
from argparse import ArgumentParser
import PIL.Image

file_server_url = "http://127.0.0.1:8000"

def create_text_to_image_prompt():
  fname = "prompts/text-to-image-sdxl-turbo.json"
  with open(fname, "r") as f:
    prompt = json.load(f)

  prompt["20"]["inputs"]["ckpt_name"] = "sd_xl_turbo_1.0_fp16.safetensors"
  prompt["5"]["inputs"]["width"] = 1024
  prompt["5"]["inputs"]["height"] = 576
  prompt["6"]["inputs"]["text"] = "A cat meditating in front of a temple, anime"

  return prompt, []

def create_image_to_video_prompt():
  fname = "prompts/image-to-video-svd.json"
  with open(fname, "r") as f:
    prompt = json.load(f)

  image_file = "image.png"
  image_path = f"files/{image_file}"
  if not os.path.exists(image_file):
    image_url = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/svd/rocket.png?download=true"
    image = PIL.Image.open(requests.get(image_url, stream=True).raw)
    image.save(image_path)

  image_file_url = f"{file_server_url}/file/{image_file}"

  prompt["15"]["inputs"]["ckpt_name"] = "svd_xt.safetensors"
  prompt["23"]["inputs"]["image"] = image_file

  return prompt, [image_file_url]

if __name__ == "__main__":
  parser = ArgumentParser()
  parser.add_argument("-j", "--job", default="text-to-image", help="the job type to run (text-to-image, image-to-video)")
  args = parser.parse_args()

  match args.job:
    case "text-to-image":
      prompt, input_files = create_text_to_image_prompt()
    case "text-to-video":
      prompt, input_files = create_image_to_video_prompt()
    case _:
      raise Exception("invalid job")

  tmp_prompt_file = tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".json", dir="files")
  json.dump(prompt, tmp_prompt_file)
  tmp_prompt_file.close()

  prompt_file_url = f"{file_server_url}/file/{Path(tmp_prompt_file.name).name}"

  data = {
    "input": {
      "prompt_file": prompt_file_url
    },
    "output_file_prefix": file_server_url + "/file/"
  }

  if len(input_files) > 0:
    data["input"]["input_files"] = input_files

  url = "http://localhost:5000/predictions"
  result = requests.post(url, json=data)
  print(result.json())

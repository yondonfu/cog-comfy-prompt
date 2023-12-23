#!/bin/bash

mkdir -p checkpoints
wget -O checkpoints/sd_xl_turbo_1.0_fp16.safetensors https://huggingface.co/stabilityai/sdxl-turbo/resolve/main/sd_xl_turbo_1.0_fp16.safetensors?download=true
wget -O checkpoints/svd_xt.safetensors https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt/resolve/main/svd_xt.safetensors?download=true
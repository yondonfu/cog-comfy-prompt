# cog-comfy-prompt

## Build

Install the latest beta release of [Cog](https://github.com/replicate/cog).

Download checkpoints.

```
./dl-checkpoints.sh
```

Build the Cog container.

```
cog build --separate-weights -t cog-comfy-prompt
```

## Run

```
docker run --network="host" --gpus all cog-comfy-prompt
```

## Test

Install dependencies.

```
pip install -r requirements.txt
```

Run the test server:

```
uvicorn test_server:app --reload
```

The test server receives GET requests for input files and PUT requests to upload output files from the Cog container.

Run the test script to generate an image using SDXL Turbo:

```
python test.py -j text-to-image
```

Run the test script to generate a video using SVD:

```
python test.py -j image-to-video
```
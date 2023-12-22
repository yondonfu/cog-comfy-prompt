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
docker run -p 5000:5000 --gpus all cog-comfy-prompt
```
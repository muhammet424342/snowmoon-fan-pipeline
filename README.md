# Snowmoon — unofficial fan clip (ch. 30, "DOG")

An 8-second, silent fan clip of one scene from *Snowmoon* by Vitalik Buterin
(https://vitalik.eth.limo/snowmoon/, GPL v3). Veridian snow drones wear paper sheets with
squiggles and a huge "DOG", and the Arctic drones fail to classify them.

**Unofficial.** Not affiliated with, endorsed by, or approved by Vitalik Buterin, the
Ethereum Foundation, or any related organization. See `NOTICE`.

## License
GPL-3.0 (`LICENSE`). Following the book's license note, the whole pipeline is open:
scene scripts, texture generator, direction notes, camera/light settings. If you build on
it, keep your pipeline open too.

## Contents
```
NOTICE, LICENSE
prompts/scene_dog.md      direction notes (no generative models were used)
blender/make_paper.py     DOG paper texture (PIL, seed 30)
blender/scene_dog.py      builds the scene from primitives
blender/animate_dog.py    keys the 8 s animation, renders frames, edits to mp4 (VSE)
blender/render.sh         one-line headless render
blender/scene_dog.blend   saved scene
out/still_dog_v2.png      approved still
out/dog_v1.mp4            the clip
```

## Render
```sh
BLENDER="/path/to/blender" sh blender/render.sh
```
Runs `make_paper.py`, then `blender -b -P scene_dog.py -P animate_dog.py -- --render`,
which writes `out/frames_dog/f0001–f0192.png` and `out/dog_v1.mp4`.

| Setting | Value |
|---|---|
| Blender | 5.2.1 LTS |
| Engine | Cycles, GPU (first available of OPTIX/CUDA/HIP/METAL/ONEAPI; HIP on the reference machine) |
| Samples | 32 per frame (clip), 96 (stills), denoiser on |
| Seed | 30 (Cycles seed, texture seed, tree scatter seed) |
| Resolution / fps | 1920×1080, 24 fps, 192 frames (8 s) |
| Color | AgX, look "Medium High Contrast", exposure +0.35; edit scene uses Standard |
| Fog | bounded volume box, density 0.012 (a world volume renders black) |
| Output | H.264 MP4, no audio |
| Models | none — no generative image/video/3D models; primitives only |
| Fonts | Arial Bold (paper), Bahnschrift (end text); Windows paths in the scripts, swap on other OSes |

Reference render time: ~23 s/frame on an AMD RX 6500 XT (HIP), ~75 min for 192 frames.

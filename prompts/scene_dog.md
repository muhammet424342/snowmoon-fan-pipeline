# scene_dog — direction notes (the "prompts" of this clip)

No generative image/video model was used. The clip is built from Blender primitives by
`blender/scene_dog.py` and `blender/animate_dog.py`, with a paper texture from
`blender/make_paper.py`. These notes are the instructions the scene was built from,
kept here because the GPL-3.0 condition asks for all non-commodity materials to be open.

## Source
Snowmoon, chapter 30 (https://vitalik.eth.limo/snowmoon/). Veridian snow drones get large
paper sheets stuck on every side: colorful squiggles plus a huge "DOG". The patterns were
optimized by querying the Arctic simulator's API (no stolen weights) so the Arctic
classifier fails to notice the drones.

## Brief (summary)
- Unofficial fan adaptation. No endorsement implied. No token / mint / official collection.
- 6–8 s. Max 8 words on screen. Cold, readable: snow, paper, typography. No neon.
- No DecayLabs branding inside the clip.

## Approved still (still_dog_v2), after one correction round
1. Hero is a drone: low hull, short skids, two small rotors on top. Paper glued flush to the
   hull side (not a separate sign). DOG readable at a glance.
2. Arctic trio: same drone family, 75% size, further back. No lamp posts. Sensor = thin
   horizontal amber strip on the front of the hull.
3. Hero out of tree shadow; light falls on the DOG paper; ground stays white.
4. Same low-poly style, no added detail.

## Timing (8 s, 24 fps, 192 frames)
- 0–1.5 s: still_dog_v2 framing, hero rotors turn slowly (1 turn / 2 s).
- 1.5–4 s: camera eases 3.5% toward its target; DOG stays readable.
- 4–6.5 s: the three Arctic drones slow down slightly (0.5 → 0.2 m/s), amber strip constant.
- 6.5–8 s: fade to snow; only text: `unofficial fan clip`.

## Notes / known limits
- The paper is a hand-made stand-in for an adversarial patch, not an optimized one.
- Rotor discs are round, so their spin is subtle by design (no new blade objects added).

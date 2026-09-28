# Snowmoon DOG clip - animation + edit. Runs AFTER scene_dog.py (same Blender session).
# 8 s, 24 fps, 192 frames. Model is untouched; only transforms are keyed.
#   0-1.5s  : still_dog_v2 framing, hero rotors turn slowly
#   1.5-4s  : camera eases in a little, DOG stays readable
#   4-6.5s  : the three Arctic drones slow down slightly (amber strip constant)
#   6.5-8s  : fade to snow, text "unofficial fan clip"
# Usage inside Blender:
#   exec(scene_dog.py); exec(animate_dog.py)      -> keys the scene
#   render_frames()                                -> out/frames_dog/f####.png
#   edit_to_mp4()                                  -> out/dog_v1.mp4 (VSE: fade + text)
import bpy, math, os, sys
from mathutils import Vector

_HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else r"C:\Users\Muhammet\code\snowmoon-fan-pipeline\blender"
ROOT = os.path.dirname(_HERE)
FRAMES = os.path.join(ROOT, "out", "frames_dog")
MP4 = os.path.join(ROOT, "out", "dog_v1.mp4")
FPS, N = 24, 192
TEXT = "unofficial fan clip"
FONT = r"C:\Windows\Fonts\bahnschrift.ttf"
SNOW_RGB = (0.93, 0.94, 0.97)

sc = bpy.context.scene
sc.frame_start, sc.frame_end, sc.render.fps = 1, N, FPS

def smooth(a, b, t):  # smoothstep of t between a and b
    x = min(max((t - a) / (b - a), 0.0), 1.0)
    return x * x * (3 - 2 * x)

# hero rotors: 1 turn per 2 s
rotors = [o for o in bpy.data.objects if o.name.startswith("VeridianDrone_Rotor")]
# camera: ease 3.5% toward its target between 1.5 s and 4 s
cam, tgt = bpy.data.objects["Cam"], bpy.data.objects["CamTarget"]
c0, aim = cam.location.copy(), tgt.location.copy()
# Arctic trio: creep forward 0.5 m/s, ease down to 0.2 m/s between 4 s and 6.5 s
arctics = [bpy.data.objects[n] for n in ("Arctic1", "Arctic2", "Arctic3")]
starts = {o.name: o.location.copy() for o in arctics}

def dist(t, v0=0.5, v1=0.2, t0=4.0, t1=6.5):
    if t <= t0:
        return v0 * t
    if t <= t1:
        u = t - t0
        return v0 * t0 + v0 * u + (v1 - v0) * u * u / (2 * (t1 - t0))
    return dist(t1) + v1 * (t - t1)

for f in range(1, N + 1):
    t = (f - 1) / FPS
    for r in rotors:
        r.rotation_euler.z = t * math.pi
        r.keyframe_insert("rotation_euler", index=2, frame=f)
    cam.location = c0.lerp(aim, 0.035 * smooth(1.5, 4.0, t))
    cam.keyframe_insert("location", frame=f)
    for o in arctics:
        yaw = o.rotation_euler.z
        o.location = starts[o.name] + Vector((math.cos(yaw), math.sin(yaw), 0)) * dist(t)
        o.keyframe_insert("location", frame=f)
sc.frame_set(1)

def render_frames(samples=32, blocking=False):
    os.makedirs(FRAMES, exist_ok=True)
    sc.cycles.samples = samples
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = os.path.join(FRAMES, "f")
    if blocking:  # headless (blender -b)
        return bpy.ops.render.render(animation=True)
    return bpy.ops.render.render("INVOKE_DEFAULT", animation=True)  # GUI: non-blocking

def edit_to_mp4():
    files = sorted(x for x in os.listdir(FRAMES) if x.endswith(".png"))
    ed = bpy.data.scenes.get("DogEdit") or bpy.data.scenes.new("DogEdit")
    ed.render.resolution_x, ed.render.resolution_y, ed.render.resolution_percentage = 1920, 1080, 100
    ed.render.fps, ed.frame_start, ed.frame_end = FPS, 1, N
    ed.view_settings.view_transform = "Standard"
    se = ed.sequence_editor_create()
    for s in list(se.strips):
        se.strips.remove(s)
    img = se.strips.new_image("frames", os.path.join(FRAMES, files[0]), 1, 1, fit_method="FIT")
    for x in files[1:]:
        img.elements.append(x)
    f_fade = int(6.5 * FPS) + 1                      # 157
    snow = se.strips.new_effect("snow", "COLOR", 2, f_fade, length=N - f_fade + 1)
    snow.color = SNOW_RGB
    snow.blend_alpha = 0.0; snow.keyframe_insert("blend_alpha", frame=f_fade)
    snow.blend_alpha = 1.0; snow.keyframe_insert("blend_alpha", frame=f_fade + 20)
    f_txt = f_fade + 8
    txt = se.strips.new_effect("label", "TEXT", 3, f_txt, length=N - f_txt + 1)
    txt.text = TEXT
    txt.font = bpy.data.fonts.load(FONT, check_existing=True)
    txt.font_size = 46
    txt.color = (0.18, 0.2, 0.24, 1.0)
    txt.location = (0.5, 0.5)
    txt.alignment_x = "CENTER"
    txt.blend_alpha = 0.0; txt.keyframe_insert("blend_alpha", frame=f_txt)
    txt.blend_alpha = 1.0; txt.keyframe_insert("blend_alpha", frame=f_txt + 16)
    ed.render.image_settings.media_type = "VIDEO"
    ed.render.image_settings.file_format = "FFMPEG"
    ed.render.ffmpeg.format, ed.render.ffmpeg.codec = "MPEG4", "H264"
    ed.render.ffmpeg.constant_rate_factor = "HIGH"
    ed.render.ffmpeg.audio_codec = "NONE"
    ed.render.filepath = MP4
    bpy.ops.render.render(animation=True, scene=ed.name)
    return MP4

if "--render" in sys.argv:  # headless: blender -b -P scene_dog.py -P animate_dog.py -- --render
    render_frames(blocking=True)
    edit_to_mp4()

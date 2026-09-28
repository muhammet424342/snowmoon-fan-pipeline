# Snowmoon (unofficial fan clip) - ch. 30 "DOG" scene. Blender 5.2, Cycles.
# Builds the whole scene from primitives (no downloaded assets, no AI models).
# Run inside Blender:  exec(open(r"<repo>/blender/scene_dog.py").read())
# or headless:        blender -b -P blender/scene_dog.py -- --still
import bpy, bmesh, math, os, random, sys
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else r"C:\Users\Muhammet\code\snowmoon-fan-pipeline\blender"
ROOT = os.path.dirname(HERE)
PAPER = os.path.join(HERE, "tex", "paper_dog.png")
SEED = 30
STILL_OUT = os.path.join(ROOT, "out", "still_dog_v1.png")

rnd = random.Random(SEED)

# ---------- reset (keep addons alive: no factory reset) ----------
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.images, bpy.data.curves):
    for b in list(coll):
        if b.users == 0:
            coll.remove(b)
sc = bpy.context.scene

def mat(name, color, rough=0.7, emit=None, emit_strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = emit_strength
    return m

SNOW = mat("Snow", (0.86, 0.9, 0.97), 0.55)
PINE = mat("Pine", (0.025, 0.06, 0.045), 0.8)
BARK = mat("Bark", (0.05, 0.035, 0.03), 0.9)
HULL = mat("Hull", (0.16, 0.17, 0.17), 0.65)          # Veridian craft: matte grey
DARK = mat("Arctic", (0.02, 0.025, 0.035), 0.35)       # Arctic craft: near-black
EYE = mat("ArcticEye", (0.0, 0.0, 0.0), 0.5, emit=(1.0, 0.55, 0.18), emit_strength=14.0)

def paper_mat():
    m = bpy.data.materials.new("PaperDOG")
    m.use_nodes = True
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(PAPER, check_existing=True)
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.85
    return m
PAPER_M = paper_mat()

def obj_from_bm(name, bm, mats):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    for m in mats:
        me.materials.append(m)
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    return o

def box(bm, size, loc, mi=0):
    r = bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(loc) @ Matrix.Diagonal((*size, 1)))
    for v in r["verts"]:
        for f in v.link_faces:
            f.material_index = mi

# ---------- world: dawn gradient + thin fog ----------
w = bpy.data.worlds.new("Dawn"); sc.world = w; w.use_nodes = True
wn = w.node_tree.nodes; wl = w.node_tree.links
bg = next(n for n in wn if n.type == "BACKGROUND")
tc = wn.new("ShaderNodeTexCoord"); sep = wn.new("ShaderNodeSeparateXYZ")
ramp = wn.new("ShaderNodeValToRGB")
wl.new(tc.outputs["Generated"], sep.inputs[0]); wl.new(sep.outputs["Z"], ramp.inputs["Fac"])
e = ramp.color_ramp.elements
e[0].position, e[0].color = 0.0, (0.55, 0.45, 0.42, 1)    # horizon: pale dawn
e[1].position, e[1].color = 0.35, (0.06, 0.1, 0.22, 1)    # zenith: deep blue
wl.new(ramp.outputs["Color"], bg.inputs["Color"]); bg.inputs["Strength"].default_value = 0.9
# NOTE: world-volume fog swallows sun + sky (renders black). Fog is a bounded box instead.
bpy.ops.mesh.primitive_cube_add(size=1, location=(20, 0, 12)); fog = bpy.context.active_object
fog.name = "FogBox"; fog.scale = (150, 150, 24)
fm = bpy.data.materials.new("Fog"); fm.use_nodes = True; fn = fm.node_tree.nodes
for nd in list(fn):
    if nd.type == "BSDF_PRINCIPLED": fn.remove(nd)
fv = fn.new("ShaderNodeVolumeScatter"); fv.inputs["Density"].default_value = 0.012
fv.inputs["Color"].default_value = (0.8, 0.85, 0.95, 1)
fm.node_tree.links.new(fv.outputs[0], next(nd for nd in fn if nd.type == "OUTPUT_MATERIAL").inputs["Volume"])
fog.data.materials.append(fm)

sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
sun.data.energy = 5.5; sun.data.color = (1.0, 0.72, 0.5); sun.data.angle = math.radians(2)
sun.rotation_euler = (math.radians(76), 0, math.radians(-30))    # low, from behind camera-left: lights the paper
sc.collection.objects.link(sun)

# ---------- ground ----------
bpy.ops.mesh.primitive_plane_add(size=300, location=(0, 0, 0))
g = bpy.context.active_object; g.name = "Ground"; g.data.materials.append(SNOW)
sub = g.modifiers.new("sub", "SUBSURF"); sub.subdivision_type = "SIMPLE"; sub.levels = sub.render_levels = 6
tex = bpy.data.textures.new("dunes", "CLOUDS"); tex.noise_scale = 6.0
dsp = g.modifiers.new("disp", "DISPLACE"); dsp.texture = tex; dsp.strength = 0.35; dsp.mid_level = 0.5

# ---------- pine prototype (shared mesh) ----------
bm = bmesh.new()
r = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.12, radius2=0.1, depth=1.2, matrix=Matrix.Translation((0, 0, 0.6)))
for f in {f for v in r["verts"] for f in v.link_faces}: f.material_index = 2
for i, (rad, z) in enumerate([(1.5, 1.6), (1.15, 2.8), (0.8, 3.9), (0.45, 4.8)]):
    r = bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=rad, radius2=0.0, depth=1.9, matrix=Matrix.Translation((0, 0, z)))
    for f in {f for v in r["verts"] for f in v.link_faces}: f.material_index = 0
    r = bmesh.ops.create_cone(bm, cap_ends=False, segments=12, radius1=rad * 0.62, radius2=0.0, depth=1.0, matrix=Matrix.Translation((0, 0, z + 0.5)))
    for f in {f for v in r["verts"] for f in v.link_faces}: f.material_index = 1
pine_me = bpy.data.meshes.new("PineMesh"); bm.to_mesh(pine_me); bm.free()
for m in (PINE, SNOW, BARK): pine_me.materials.append(m)

def in_clearing(x, y):
    # corridor + sun-side sector kept empty so no tree shadow lands on the hero
    return (-14 < x < 45 and abs(y) < 7) or (-45 < x < 6 and -45 < y < 0)
n = 0
while n < 260:
    x, y = rnd.uniform(-40, 90), rnd.uniform(-45, 45)
    if in_clearing(x, y):
        continue
    p = bpy.data.objects.new(f"Pine{n:03d}", pine_me)
    s = rnd.uniform(1.3, 2.6)
    p.location = (x, y, -0.1); p.scale = (s, s, s * rnd.uniform(0.9, 1.25)); p.rotation_euler.z = rnd.uniform(0, 6.28)
    sc.collection.objects.link(p); n += 1

# ---------- drone family (hero + Arctic share one builder) - front = local +X ----------
def drone(name, mats, sensor=False):
    bm = bmesh.new()
    box(bm, (2.4, 1.2, 0.8), (0, 0, 0.65), 0)            # low hull
    box(bm, (0.5, 1.0, 0.5), (1.4, 0, 0.5), 0)           # nose
    for yy in (-0.5, 0.5):
        box(bm, (1.9, 0.14, 0.08), (0.1, yy, 0.08), 0)   # short skids
        for xx in (-0.6, 0.7):
            box(bm, (0.07, 0.07, 0.24), (xx, yy, 0.2), 0)
    for xx in (-0.7, 0.7):                              # rotor posts
        box(bm, (0.08, 0.08, 0.2), (xx, 0, 1.15), 0)
    if sensor:                                           # thin horizontal amber strip, front of hull
        box(bm, (0.03, 0.9, 0.06), (1.66, 0, 0.55), 1)
    o = obj_from_bm(name, bm, mats)
    b = o.modifiers.new("bev", "BEVEL"); b.width = 0.03; b.segments = 2
    for i, xx in enumerate((-0.7, 0.7)):                 # rotor discs: own objects so they can spin
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.45, radius2=0.45, depth=0.04)
        r = obj_from_bm(f"{name}_Rotor{i}", bm, mats[:1])
        r.location = (xx, 0, 1.27); r.parent = o
        b = r.modifiers.new("bev", "BEVEL"); b.width = 0.03; b.segments = 2
    return o

hero = drone("VeridianDrone", [HULL])
HERO_YAW = math.radians(-10)

def paper(name, w_, h_, loc, rot):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name
    o.scale = (w_, h_, 1); o.data.materials.append(PAPER_M)
    return o
# glued flush to the hull faces (hull half-width 0.6, center z 0.65)
paper("PaperSide", 1.25, 0.74, (-0.1, -0.604, 0.65), (math.radians(90), 0, 0))
paper("PaperSideR", 1.25, 0.74, (-0.1, 0.604, 0.65), (math.radians(90), 0, math.radians(180)))
paper("PaperNose", 0.78, 0.46, (1.654, 0, 0.5), (math.radians(90), 0, math.radians(90)))
for nm in ("PaperSide", "PaperSideR", "PaperNose"):
    bpy.data.objects[nm].parent = hero
hero.rotation_euler.z = HERO_YAW

# ---------- Arctic trio: same family, smaller, further back, face -X ----------
def arctic(name, loc, yaw):
    o = drone(name, [DARK, EYE], sensor=True)
    o.location = loc; o.scale = (0.75, 0.75, 0.75); o.rotation_euler.z = math.radians(180 + yaw)
    return o
arctic("Arctic1", (13, 3.0, 0), 0)
arctic("Arctic2", (16.5, -0.6, 0), 32)     # turned away: misclassified, line breaks
arctic("Arctic3", (20, 2.2, 0), -18)

# ---------- camera ----------
target = bpy.data.objects.new("CamTarget", None); target.location = (3.0, 0.3, 0.3)
sc.collection.objects.link(target)
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
cam.data.lens = 32; cam.location = (-5.0, -5.8, 2.5)
tt = cam.constraints.new("TRACK_TO"); tt.target = target
sc.collection.objects.link(cam); sc.camera = cam

# ---------- render ----------
sc.render.engine = "CYCLES"
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.get_devices()
    for dev_type in ("OPTIX", "CUDA", "HIP", "METAL", "ONEAPI"):  # first type that has a real GPU
        try:
            prefs.compute_device_type = dev_type
        except TypeError:
            continue
        prefs.get_devices()
        gpus = [d for d in prefs.devices if d.type == dev_type]
        if gpus:
            for d in gpus: d.use = True
            break
    sc.cycles.device = "GPU"
except Exception:
    pass
sc.cycles.samples = 96; sc.cycles.use_denoising = True; sc.cycles.seed = SEED
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 100
sc.render.fps = 24
try:
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.view_settings.exposure = 0.35
except TypeError:
    pass
sc.render.image_settings.file_format = "PNG"

if "--still" in sys.argv or os.environ.get("DOG_STILL"):
    sc.render.filepath = STILL_OUT
    bpy.ops.render.render(write_still=True)
    print("STILL", STILL_OUT)

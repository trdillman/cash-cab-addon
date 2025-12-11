"""
Unified Blender Operations
"""
import bpy
import json
import math
import random
from bpy.props import *
from bpy.app.handlers import persistent

# Import Engines
from .engine_v2 import core as v2_core
from .engine_v2 import solver as v2_solver
from .engine_v2 import director as v2_director
from .engine_viz import logic as viz_logic

# -------------------------------------------------------------------
# 1. LIVE UPDATE LOGIC (V2 ENGINE)
# -------------------------------------------------------------------

def update_v2_engine(settings, context):
    """Runs the V2 Solver and updates the cached plan."""
    if not settings.v2_cached_samples:
        return
        
    try:
        data = json.loads(settings.v2_cached_samples)
        samples = []
        for s in data['samples']:
            p = v2_core.Vector(s['p'])
            t = v2_core.Vector(s['t'])
            samples.append(v2_core.CurveSample(p, t, None, None, 0, 0, s['u']))
        total_len = data['total_len']
        ctx = v2_solver.AnalyzeContext(samples, total_len)
    except Exception as e:
        print(f"RouteCam V2 Engine JSON Error: {e}")
        return

    # Solve
    try:
        config = {
            'margin': settings.margin,
            'zoom_ratio': settings.zoom_ratio,
            'pitch_start': math.radians(settings.pitch_start),
            'pitch_end': math.radians(settings.pitch_end),
            'yaw_offset': math.radians(settings.yaw_offset),
            'establish_end': settings.beat_drift
        }
        
        beats = {
            'establish': 0.0, 
            'drift_start': settings.beat_drift, 
            'zoom_start': settings.beat_zoom, 
            'chase': 1.0
        }
        
        frames = settings.duration
        d = v2_director.Director(frames, beats)
        
        plan = []
        for f in range(frames + 1):
            sigma = d.get_sigma(f, 0)
            target, scale, view = v2_solver.solve_framing(ctx, sigma, config)
            plan.append({
                'frame': f,
                'target': target.to_tuple(),
                'scale': scale,
                'view': view.to_tuple()
            })
            
        settings.v2_cached_plan = json.dumps(plan)
        
        # Trigger Viewport Update
        if context.screen:
            for area in context.screen.areas: area.tag_redraw()
        
        # Apply to current frame
        apply_v2_frame(context.scene)
    except Exception as e:
        print(f"RouteCam V2 Solver Error: {e}")
        import traceback
        traceback.print_exc()

def apply_v2_frame(scene):
    cam = scene.camera
    if not cam: return
    settings = cam.routecam_unified
    
    if settings.engine_mode != 'V2' or not settings.v2_cached_plan:
        return
        
    try:
        plan = json.loads(settings.v2_cached_plan)
        rel = scene.frame_current - scene.frame_start
        idx = max(0, min(len(plan)-1, rel))
        kf = plan[idx]
        
        # Apply
        cam.data.ortho_scale = kf['scale']
        
        target = v2_core.Vector(kf['target'])
        view = v2_core.Vector(kf['view'])
        
        cam.location = (target - view * kf['scale']*2.0).to_tuple()
        
        import mathutils
        mv = mathutils.Vector(kf['view'])
        cam.rotation_mode = 'QUATERNION'
        cam.rotation_quaternion = mv.to_track_quat('-Z', 'Y')
        
    except:
        pass

@persistent
def frame_handler(scene):
    apply_v2_frame(scene)

# -------------------------------------------------------------------
# 2. CALLBACKS & OPERATORS
# -------------------------------------------------------------------

def update_callback(self, context):
    """Master callback for all properties."""
    if self.engine_mode == 'V2':
        update_v2_engine(self, context)
    elif self.engine_mode == 'VIZ':
        # Viz engine bakes immediately
        cam = context.active_object
        if cam and cam.type == 'CAMERA':
            viz_logic.run_generation(cam, self)

class ROUTECAM_OT_Generate(bpy.types.Operator):
    bl_idname = "routecam.generate"
    bl_label = "Analyze / Generate"
    
    def execute(self, context):
        cam = context.active_object
        if not cam or cam.type != 'CAMERA': return {'CANCELLED'}
        settings = cam.routecam_unified
        
        curve = settings.target_curve
        if not curve: return {'CANCELLED'}
        
        if settings.engine_mode == 'V2':
            # 1. Heavy Analysis
            deps = context.evaluated_depsgraph_get()
            eval_obj = curve.evaluated_get(deps)
            mesh = eval_obj.to_mesh()
            verts = [v.co for v in mesh.vertices]
            eval_obj.to_mesh_clear()
            
            mw = curve.matrix_world
            pts = [v2_core.Vector(mw @ v) for v in verts]
            
            samples, length = v2_core.sample_curve_with_metrics(pts, 200)
            
            # Cache
            s_data = [{'p': s.position.to_tuple(), 't': s.tangent.to_tuple(), 'u': s.u} for s in samples]
            settings.v2_cached_samples = json.dumps({'samples': s_data, 'total_len': length})
            
            # 2. Run Solver
            update_v2_engine(settings, context)
            
        elif settings.engine_mode == 'VIZ':
            viz_logic.run_generation(cam, settings)
            
        return {'FINISHED'}

class ROUTECAM_OT_BakeV2(bpy.types.Operator):
    bl_idname = "routecam.bake_v2"
    bl_label = "Bake V2 to Keyframes"
    
    def execute(self, context):
        cam = context.active_object
        settings = cam.routecam_unified
        if not settings.v2_cached_plan: return {'CANCELLED'}
        
        plan = json.loads(settings.v2_cached_plan)
        start = context.scene.frame_start
        
        if cam.animation_data: cam.animation_data_clear()
        if cam.data.animation_data: cam.data.animation_data_clear()
        
        for kf in plan:
            f = start + kf['frame']
            cam.data.ortho_scale = kf['scale']
            cam.data.keyframe_insert("ortho_scale", frame=f)
            
            t = v2_core.Vector(kf['target'])
            v = v2_core.Vector(kf['view'])
            cam.location = (t - v * kf['scale']*2.0).to_tuple()
            cam.keyframe_insert("location", frame=f)
            
            import mathutils
            mv = mathutils.Vector(kf['view'])
            cam.rotation_quaternion = mv.to_track_quat('-Z', 'Y')
            cam.keyframe_insert("rotation_quaternion", frame=f)
            
        return {'FINISHED'}

class ROUTECAM_OT_RandomBatch(bpy.types.Operator):
    bl_idname = "routecam.random_batch"
    bl_label = "Generate Random Batch"
    
    def execute(self, context):
        base_cam = context.active_object
        settings = base_cam.routecam_unified
        count = settings.batch_count
        curve = settings.target_curve
        
        if not curve:
            self.report({'ERROR'}, "No target curve selected.")
            return {'CANCELLED'}
            
        # Ensure source has analysis data if in V2 mode
        if settings.engine_mode == 'V2' and not settings.v2_cached_samples:
             self.report({'ERROR'}, "Please Analyze the main camera first.")
             return {'CANCELLED'}
        
        col = bpy.data.collections.new("RouteCam_Batch")
        context.scene.collection.children.link(col)
        
        for i in range(count):
            name = f"Cam_{settings.engine_mode}_{i}"
            c_data = bpy.data.cameras.new(name)
            c_obj = bpy.data.objects.new(name, c_data)
            col.objects.link(c_obj)
            
            # Copy Settings
            s = c_obj.routecam_unified
            s.target_curve = curve
            s.engine_mode = settings.engine_mode
            s.duration = random.randint(100, 250)
            
            # Randomize based on mode
            if s.engine_mode == 'V2':
                s.margin = random.uniform(1.2, 3.0)
                s.pitch_start = random.uniform(20, 60)
                s.yaw_offset = random.uniform(-90, 90)
                s.beat_drift = random.uniform(0.1, 0.4)
                
                # Copy analysis cache
                s.v2_cached_samples = settings.v2_cached_samples
                
                # Generate Plan
                update_v2_engine(s, context) 
                
                # Bake (Safe Check)
                if not s.v2_cached_plan:
                    print(f"Skipping {name}: Plan generation failed.")
                    continue
                    
                try:
                    plan = json.loads(s.v2_cached_plan)
                    for kf in plan:
                        f = 1 + kf['frame']
                        c_data.ortho_scale = kf['scale']
                        c_data.keyframe_insert("ortho_scale", frame=f)
                        t = v2_core.Vector(kf['target'])
                        v = v2_core.Vector(kf['view'])
                        c_obj.location = (t - v * kf['scale']*2).to_tuple()
                        c_obj.keyframe_insert("location", frame=f)
                        import mathutils
                        c_obj.rotation_quaternion = mathutils.Vector(kf['view']).to_track_quat('-Z', 'Y')
                        c_obj.keyframe_insert("rotation_quaternion", frame=f)
                except Exception as e:
                    print(f"Batch Bake Error on {name}: {e}")
                    
            elif s.engine_mode == 'VIZ':
                s.sect1_margin = random.uniform(1.2, 3.0)
                s.sect1_angle = random.uniform(-90, 90)
                s.sect2_time = random.uniform(0.2, 0.5)
                viz_logic.run_generation(c_obj, s)
                
        return {'FINISHED'}

# -------------------------------------------------------------------
# 3. PROPERTIES & UI
# -------------------------------------------------------------------

class RouteCamUnifiedSettings(bpy.types.PropertyGroup):
    # Shared
    target_curve = PointerProperty(type=bpy.types.Object, name="Route", update=update_callback)
    duration = IntProperty(name="Duration", default=120, update=update_callback)
    engine_mode = EnumProperty(
        name="Engine",
        items=[('V2', "Robust Director (v2)", "Solver-based, non-destructive"),
               ('VIZ', "Keyframe Viz (v3)", "Direct curves, visualization path")],
        default='V2', update=update_callback
    )
    
    # V2 Params
    margin = FloatProperty(name="Margin", default=1.9, update=update_callback)
    zoom_ratio = FloatProperty(name="Zoom", default=0.06, update=update_callback)
    pitch_start = FloatProperty(name="Start Pitch", default=30.0, update=update_callback)
    pitch_end = FloatProperty(name="End Pitch", default=15.0, update=update_callback)
    yaw_offset = FloatProperty(name="Start Yaw", default=-75.0, update=update_callback)
    beat_drift = FloatProperty(name="Drift %", default=0.2, update=update_callback)
    beat_zoom = FloatProperty(name="Zoom %", default=0.4, update=update_callback)
    v2_cached_samples = StringProperty()
    v2_cached_plan = StringProperty()

    # Viz Params (Mappings)
    # We map these to the Viz logic names
    sect1_margin = FloatProperty(name="Start Scale", default=1.5, update=update_callback)
    sect1_angle = FloatProperty(name="Start Angle", default=-70.0, update=update_callback)
    sect1_pitch = FloatProperty(name="Start Pitch", default=60.0, update=update_callback)
    sect2_time = FloatProperty(name="Drift Time", default=0.3, update=update_callback)
    sect2_push = FloatProperty(name="Drift Push", default=0.1, update=update_callback)
    sect3_zoom = FloatProperty(name="End Scale", default=0.08, update=update_callback)
    sect3_angle = FloatProperty(name="End Angle", default=0.0, update=update_callback)
    sect3_pitch = FloatProperty(name="End Pitch", default=73.0, update=update_callback)
    sect3_offset_x = FloatProperty(name="Off X", default=0.0, update=update_callback)
    sect3_offset_y = FloatProperty(name="Off Y", default=0.0, update=update_callback)
    rot_power = FloatProperty(name="Rot Power", default=1.0, update=update_callback)
    optimize_keys = BoolProperty(name="Optimize", default=True) # Not used in callback, baked on generate
    
    # Batch
    batch_count = IntProperty(name="Batch Count", default=5, min=1)

class ROUTECAM_PT_Unified(bpy.types.Panel):
    bl_label = "RouteCam Ultimate"
    bl_idname = "ROUTECAM_PT_Unified"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'RouteCam'
    
    def draw(self, context):
        layout = self.layout
        cam = context.active_object
        if not cam or cam.type != 'CAMERA':
            layout.label(text="Select a Camera")
            return
            
        s = cam.routecam_unified
        
        # Engine Select
        row = layout.row()
        row.prop(s, "engine_mode", expand=True)
        
        layout.separator()
        layout.prop(s, "target_curve")
        layout.prop(s, "duration")
        
        # Dynamic UI
        if s.engine_mode == 'V2':
            box = layout.box()
            box.label(text="Robust Director Settings")
            box.prop(s, "margin")
            box.prop(s, "zoom_ratio")
            col = box.column(align=True)
            col.prop(s, "pitch_start")
            col.prop(s, "pitch_end")
            col.prop(s, "yaw_offset")
            col = box.column(align=True)
            col.prop(s, "beat_drift")
            col.prop(s, "beat_zoom")
            
            layout.operator("routecam.generate", text="Analyze & Preview", icon='FILE_REFRESH')
            if s.v2_cached_plan:
                layout.operator("routecam.bake_v2", text="Bake Final", icon='ACTION')
                
        elif s.engine_mode == 'VIZ':
            box = layout.box()
            box.label(text="Keyframe Viz Settings")
            box.prop(s, "sect1_margin")
            box.prop(s, "sect1_angle")
            box.prop(s, "sect2_time")
            box.prop(s, "sect2_push")
            
            layout.operator("routecam.generate", text="Generate (Direct Bake)", icon='FILE_REFRESH')
            
        # Batch
        layout.separator()
        box = layout.box()
        box.label(text="Batch Generation")
        box.prop(s, "batch_count")
        box.operator("routecam.random_batch", icon='DUPLICATE')

# -------------------------------------------------------------------
# REGISTRATION
# -------------------------------------------------------------------

classes = (
    RouteCamUnifiedSettings,
    ROUTECAM_OT_Generate,
    ROUTECAM_OT_BakeV2,
    ROUTECAM_OT_RandomBatch,
    ROUTECAM_PT_Unified
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.routecam_unified = PointerProperty(type=RouteCamUnifiedSettings)
    
    if frame_handler not in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.append(frame_handler)

def unregister():
    if frame_handler in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.remove(frame_handler)
    del bpy.types.Object.routecam_unified
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

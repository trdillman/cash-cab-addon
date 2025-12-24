import bpy
import json
import os
from mathutils import Vector, Color

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "render_config.json")


def _set_if_attr(obj, attr_names, value, label):
    """Set the first existing attribute in attr_names on obj to value.

    Logs a warning if none of the candidate attributes exist. Returns the
    attribute name that was set or None if no attribute was updated.
    """
    for name in attr_names:
        if hasattr(obj, name):
            try:
                setattr(obj, name, value)
                return name
            except Exception as exc:
                print(f"[BLOSM] WARN render: failed to set {label} via {name}: {exc}")
                return None
    print(f"[BLOSM] WARN render: missing attr(s) for {label}: {attr_names}")
    return None

def load_config():
    if not os.path.exists(CONFIG_PATH):
        print(f"[BLOSM] Render config not found at {CONFIG_PATH}")
        return None
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def apply_render_settings(context):
    data = load_config()
    if not data:
        return

    scene = context.scene
    print("[BLOSM] Applying definitive render settings...")

    # --- Render Settings ---
    r_data = data.get("render", {})
    scene.render.engine = r_data.get("engine", "CYCLES")
    scene.render.resolution_x = r_data.get("resolution_x", 1920)
    scene.render.resolution_y = r_data.get("resolution_y", 1080)
    scene.render.resolution_percentage = 100
    scene.render.fps = r_data.get("fps", 24)
    scene.render.fps_base = r_data.get("fps_base", 1.0)
    scene.render.pixel_aspect_x = r_data.get("pixel_aspect_x", 1.0)
    scene.render.pixel_aspect_y = r_data.get("pixel_aspect_y", 1.0)
    scene.render.use_border = r_data.get("use_border", False)
    scene.render.use_compositing = r_data.get("use_compositing", True)
    scene.render.use_sequencer = r_data.get("use_sequencer", False)
    scene.render.film_transparent = r_data.get("film_transparent", False)
    scene.render.filter_size = r_data.get("filter_size", 1.5)

    img = r_data.get("image_settings", {})
    scene.render.image_settings.file_format = img.get("file_format", 'PNG')
    scene.render.image_settings.color_mode = img.get("color_mode", 'RGBA')
    scene.render.image_settings.color_depth = img.get("color_depth", '8')
    scene.render.image_settings.compression = img.get("compression", 15)
    scene.render.image_settings.quality = img.get("quality", 90)

    # --- Cycles Settings ---
    if scene.render.engine == 'CYCLES':
        c_data = data.get("cycles", {})
        c = scene.cycles
        c.device = c_data.get("device", 'CPU')
        c.feature_set = c_data.get("feature_set", 'SUPPORTED')
        c.samples = c_data.get("samples", 128)
        c.preview_samples = c_data.get("preview_samples", 32)
        c.use_adaptive_sampling = c_data.get("use_adaptive_sampling", True)
        c.adaptive_threshold = c_data.get("adaptive_threshold", 0.01)
        c.adaptive_min_samples = c_data.get("adaptive_min_samples", 0)
        c.max_bounces = c_data.get("max_bounces", 12)
        c.diffuse_bounces = c_data.get("diffuse_bounces", 4)
        c.glossy_bounces = c_data.get("glossy_bounces", 4)
        c.transparent_max_bounces = c_data.get("transparent_max_bounces", 8)
        c.transmission_bounces = c_data.get("transmission_bounces", 12)
        c.volume_bounces = c_data.get("volume_bounces", 0)
        c.caustics_reflective = c_data.get("caustics_reflective", False)
        c.caustics_refractive = c_data.get("caustics_refractive", False)
        c.film_exposure = c_data.get("film_exposure", 1.0)
        c.pixel_filter_type = c_data.get("pixel_filter_type", 'BLACKMAN_HARRIS')

        # Cycles device/denoiser configuration
        # 1) Try to set the global Cycles add-on preference to OPTIX where supported.
        try:
            prefs = getattr(bpy.context, "preferences", None)
            addons = getattr(prefs, "addons", {}) if prefs else {}
            cycles_addon = addons.get("cycles") if hasattr(addons, "get") else None
            cycles_prefs = getattr(cycles_addon, "preferences", None) if cycles_addon else None
            if cycles_prefs is not None and hasattr(cycles_prefs, "compute_device_type"):
                cycles_prefs.compute_device_type = "OPTIX"
        except Exception as exc:
            print(f"[BLOSM] WARN render: could not set Cycles compute_device_type to OPTIX: {exc}")

        # 2) Denoiser and high-quality denoising settings on the scene.
        _set_if_attr(c, ["denoiser"], "OPENIMAGEDENOISE", "Cycles denoiser")
        _set_if_attr(
            c,
            ["denoising_input_passes"],
            "RGB_ALBEDO_NORMAL",
            "Cycles denoising input passes",
        )
        _set_if_attr(
            c,
            ["denoising_prefilter"],
            "ACCURATE",
            "Cycles denoising prefilter",
        )
        _set_if_attr(
            c,
            ["denoising_quality"],
            "HIGH",
            "Cycles denoising quality",
        )
        _set_if_attr(
            c,
            ["denoising_use_gpu"],
            True,
            "Cycles denoising_use_gpu",
        )

    # --- View Layer Settings ---
    vl_data = data.get("view_layer", {})
    vl = context.view_layer
    for key, val in vl_data.items():
        if hasattr(vl, key):
            setattr(vl, key, val)

    # --- Color Management ---
    cm_data = data.get("color_management", {})
    scene.display_settings.display_device = cm_data.get("display_device", 'sRGB')
    scene.view_settings.view_transform = cm_data.get("view_transform", 'Filmic')
    scene.view_settings.look = cm_data.get("look", 'None')
    scene.view_settings.exposure = cm_data.get("exposure", 0.0)
    scene.view_settings.gamma = cm_data.get("gamma", 1.0)
    scene.view_settings.use_curve_mapping = cm_data.get("use_curve_mapping", False)

    # --- Compositor (Script Execution Method) ---
    comp_data = data.get("compositor", {})
    if comp_data.get("use_nodes"):
        scene.use_nodes = True  # Ensure compositor is enabled so node_tree exists
        
        # We ignore the JSON nodes/links and use the definitive python script
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "compositor_script.py"))
        
        if os.path.exists(script_path):
            print(f"[BLOSM] Executing compositor script: {script_path}")
            try:
                # 1. Cleanup existing generated node groups to prevent duplicates
                # The script creates groups like ".RR_...", "Render Raw.001"
                cleanup_prefixes = (".RR_", "Render Raw.")
                for ng in list(bpy.data.node_groups):
                    if ng.name.startswith(cleanup_prefixes):
                        bpy.data.node_groups.remove(ng)
                
                # 2. Read and Patch Script
                with open(script_path, 'r') as f:
                    script_content = f.read()
                
                # Patch: Remove scene duplication logic and target active scene
                # The script typically starts with scene copying logic around lines 5-19
                # We'll search for the specific block to replace safely
                
                start_marker = "# Generate unique scene name"
                end_marker = "bpy.context.window.scene = scene"
                
                if start_marker in script_content and end_marker in script_content:
                    start_idx = script_content.find(start_marker)
                    end_idx = script_content.find(end_marker) + len(end_marker)
                    
                    # Replacement block: simply assign the current context scene to 'scene' variable
                    # which the rest of the script uses.
                    patch_code = "scene = bpy.context.scene\n"
                    
                    patched_script = script_content[:start_idx] + patch_code + script_content[end_idx:]
                    
                    # 3. Execute
                    # We use a restricted global dict but ensure bpy is available
                    # The script imports bpy/mathutils itself, but we provide context if needed
                    exec_globals = {
                        "bpy": bpy,
                    }
                    
                    exec(patched_script, exec_globals)
                    print("[BLOSM] Compositor script executed successfully.")
                    
                else:
                    print("[BLOSM] Warn: Could not patch COMPOSITE.py (markers not found). Executing as-is (risky).")
                    # Fallback: try executing with 'scene' injected into globals, but the script might overwrite it
                    # If markers aren't found, the file format might have changed. 
                    # We'll abort to be safe rather than creating infinite scenes.
                    print("[BLOSM] Aborting compositor script execution to prevent scene duplication.")

            except Exception as e:
                print(f"[BLOSM] Error executing compositor script: {e}")
                import traceback
                traceback.print_exc()
        else:
             print(f"[BLOSM] Compositor script not found: {script_path}")

    # --- Eevee (Fast GI, AO, clamping, tiling) ---
    eevee = getattr(scene, "eevee", None)
    if eevee is not None:
        # Fast GI: enable and set diffuse bounces
        _set_if_attr(eevee, ["use_fast_gi"], True, "Fast GI enable")
        _set_if_attr(eevee, ["gi_diffuse_bounces"], 1, "Fast GI diffuse bounces")
        # Mode: use GLOBAL_ILLUMINATION (treat as Replace in UI semantics)
        _set_if_attr(eevee, ["fast_gi_method"], "GLOBAL_ILLUMINATION", "Fast GI method")

        # Ambient Occlusion (AO): enable, factor/distance
        _set_if_attr(eevee, ["use_gtao"], True, "AO enable")
        _set_if_attr(eevee, ["gtao_distance"], 50.0, "AO distance")
        # Eevee 4.5 exposes gtao_quality as a 0-1 quality scale; use 1.0
        # to represent the maximum "factor" for AO in this context.
        _set_if_attr(eevee, ["gtao_quality"], 1.0, "AO quality")

        # Light clamping: surface direct/indirect
        _set_if_attr(eevee, ["clamp_surface_direct"], 10.0, "direct light clamp")
        _set_if_attr(eevee, ["clamp_surface_indirect"], 1.0, "indirect light clamp")

        # Tiling: there is no explicit tiling toggle in Eevee Next; treat overscan as the closest control.
        _set_if_attr(eevee, ["use_overscan"], False, "tiling/overscan")

    print("[BLOSM] Render settings applied successfully.")

class BLOSM_OT_ApplyRenderSettings(bpy.types.Operator):
    """Apply definitive render settings from config"""
    bl_idname = "blosm.apply_render_settings"
    bl_label = "Apply Render Settings"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        # Show a confirmation dialog before applying render settings
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        apply_render_settings(context)
        return {'FINISHED'}

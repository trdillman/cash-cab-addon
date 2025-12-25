import importlib.util, sys
from pathlib import Path
import bpy

def load_addon():
    repo_root = Path(__file__).resolve().parents[2]
    init_path = repo_root / '__init__.py'
    module_name='cash_cab_addon'
    if module_name in sys.modules:
        m=sys.modules[module_name]
    else:
        spec=importlib.util.spec_from_file_location(module_name,str(init_path),submodule_search_locations=[str(repo_root)])
        m=importlib.util.module_from_spec(spec)
        sys.modules[spec.name]=m
        spec.loader.exec_module(m)
    try:
        m.register()
    except Exception:
        pass

load_addon()
sc=bpy.context.scene
addon=getattr(sc,'blosm',None)
print('=== ADDON ===')
if addon:
    for k in ['route_start_address','route_end_address','route_padding_m','auto_snap_addresses','start_snapped_coords','end_snapped_coords','route_start_address_lat','route_start_address_lon','route_end_address_lat','route_end_address_lon']:
        try:
            print(k, getattr(addon,k))
        except Exception:
            print(k,'<missing>')
for k in ['blosm_anim_start','blosm_anim_end','blosm_route_start','blosm_route_end','blosm_lead_frames']:
    if hasattr(sc,k):
        print(k, getattr(sc,k))

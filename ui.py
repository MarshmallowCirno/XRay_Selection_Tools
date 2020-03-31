import bpy, rna_keymap_ui
from .keymaps import addon_keymaps


class SELBOXXRAY_preferences(bpy.types.AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Keymaps:")

        col = box.column() 
        kc = bpy.context.window_manager.keyconfigs.user
        
        def draw_keymap_items(kc, km):
            count = len([tuple for tuple in addon_keymaps if tuple[0].name == km.name]) 
            # get only first keyitems from keymap, skipping user created keymaps, that goes after addon created keyitems
            kmis = [kmi for kmi in km.keymap_items if kmi.idname in {"mesh.select_box_xray", "object.select_box_xray",\
            "mesh.select_lasso_xray", "object.select_lasso_xray", "mesh.select_circle_xray", "object.select_circle_xray"}][:count] 
            for kmi in reversed(kmis): # reverse order, as addon adds them from bottom to top
                rna_keymap_ui.draw_kmi(['ADDON', 'USER', 'DEFAULT'], kc, km, kmi, col, 0)
            
        col.label(text="Mesh")
        km = kc.keymaps.get("Mesh")
        draw_keymap_items(kc, km)
            
        col.label(text="Object")
        km = kc.keymaps.get("Object Mode")
        draw_keymap_items(kc, km)
        
        
classes = (
    SELBOXXRAY_preferences,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
import bpy
import rna_keymap_ui
from .keymaps import addon_keymaps


class SELBOXXRAY_preferences(bpy.types.AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    tabs: bpy.props.EnumProperty(
        name="Tabs",
        items=[('GENERAL', "General", ""),
               ('KEYMAP', "Keymap", "")
               ],
        default='GENERAL',
        options={'SKIP_SAVE'})
    select_through_toggle_key: bpy.props.EnumProperty(
        name="Selection Through Toggle Key",
        description="Toggle selection through by holding this key",
        items=[('CTRL', "CTRL", ""),
               ('ALT', "ALT", ""),
               ('SHIFT', "SHIFT", ""),
               ('DISABLED', "DISABLED", "")
               ],
        default='DISABLED')
    alter_mode: bpy.props.EnumProperty(
        name="Alternate Mode",
        description="Alternate selection mode",
        items=[('SET', "Set", "Set a new selection", 'SELECT_SET', 1),
               ('ADD', "Extend", "Extend existing selection", 'SELECT_EXTEND', 2),
               ('SUB', "Subtract", "Subtract existing selection", 'SELECT_SUBTRACT', 3)
               ],
        default='SUB')
    alter_mode_toggle_key: bpy.props.EnumProperty(
        name="Alternate Mode Toggle Key",
        description="Toggle selection mode by holding this key",
        items=[('CTRL', "CTRL", ""),
               ('ALT', "ALT", ""),
               ('SHIFT', "SHIFT", "")
               ],
        default='SHIFT')

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(self, "tabs", expand=True)
        box = col.box()

        if self.tabs == 'GENERAL':
            self.draw_general(box)
        elif self.tabs == 'KEYMAP':
            self.draw_keymap(box)

    def draw_general(self, box):
        row = box.row()
        row.label(text="Key operators (B, C, L) settings in edit mode")

        row = box.row()
        row.label(text="Toggle selection through by holding this key")
        row.prop(self, "select_through_toggle_key", text="")

        row = box.row()
        row.label(text="Toggle selection mode by holding this key")
        row.prop(self, "alter_mode_toggle_key", text="")

        row = box.row()
        row.label(text="Alternate selection mode")
        row.prop(self, "alter_mode", text="")

    @staticmethod
    def draw_keymap(box):
        kc = bpy.context.window_manager.keyconfigs.user
        col = box.column()

        def draw_keymap_items():
            count = len([km_tuple for km_tuple in addon_keymaps if km_tuple[0].name == km.name])
            # get only first keymap items from keymap, skipping user created keymap,
            # that goes after addon created keymap items
            kmis = [kmi for kmi in km.keymap_items if
                    kmi.idname in {"mesh.select_box_xray", "object.select_box_xray",
                                   "mesh.select_lasso_xray", "object.select_lasso_xray",
                                   "mesh.select_circle_xray", "object.select_circle_xray"}][:count]
            for kmi in kmis:
                rna_keymap_ui.draw_kmi(['ADDON', 'USER', 'DEFAULT'], kc, km, kmi, col, 0)

        col.label(text="Mesh")
        km = kc.keymaps.get("Mesh")
        draw_keymap_items()

        col.label(text="Object")
        km = kc.keymaps.get("Object Mode")
        draw_keymap_items()


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

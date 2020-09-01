import bpy
import textwrap
import rna_keymap_ui
from .keymaps import addon_keymaps


class XRAYSEL_preferences(bpy.types.AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    tabs: bpy.props.EnumProperty(
        name="Tabs",
        items=[('MESH_TOOLS', "Mesh Tools", ""),
               ('OBJECT_TOOLS', "Object Tools", ""),
               ('KEYMAP', "Advanced Keymap", "")
               ],
        default='MESH_TOOLS',
        options={'SKIP_SAVE'})

    me_select_through: bpy.props.BoolProperty(
        name="Select Through",
        description="Select verts, faces and edges laying underneath",
        default=True
    )
    me_select_through_toggle_key: bpy.props.EnumProperty(
        name="Selection Through Toggle Key",
        description="Toggle selection through by holding this key",
        items=[('CTRL', "CTRL", ""),
               ('ALT', "ALT", ""),
               ('SHIFT', "SHIFT", ""),
               ('DISABLED', "DISABLED", "")
               ],
        default='DISABLED'
    )
    me_select_through_toggle_type: bpy.props.EnumProperty(
        name="Toggle Selection Through by Press or Hold",
        description="Toggle selection through by holding or by pressing key",
        items=[('HOLD', "Holding", ""),
               ('PRESS', "Pressing", "")
               ],
        default='HOLD'
    )
    me_default_color: bpy.props.FloatVectorProperty(
        name="Default Color",
        description="Tool color when selection through is disabled",
        subtype='COLOR',
        soft_min=0.0,
        soft_max=1.0,
        size=3,
        default=(1.0, 1.0, 1.0)
    )
    me_select_through_color: bpy.props.FloatVectorProperty(
        name="Select Through Color",
        description="Tool color when selection through is disabled",
        subtype='COLOR',
        soft_min=0.0,
        soft_max=1.0,
        size=3,
        default=(1.0, 1.0, 1.0)
    )
    me_show_xray: bpy.props.BoolProperty(
        name="Show X-Ray",
        description="Enable x-ray shading during selection",
        default=True
    )
    me_select_all_edges: bpy.props.BoolProperty(
        name="Select All Edges",
        description="Additionally select edges that are partially inside the selection borders, "
                    "not just the ones completely inside the selection borders. Works only "
                    "in select through mode",
        default=False
    )
    me_select_all_faces: bpy.props.BoolProperty(
        name="Select All Faces",
        description="Additionally select faces that are partially inside the selection borders, "
                    "not just the ones with centers inside the selection borders. Works only "
                    "in select through mode",
        default=False
    )
    me_hide_mirror: bpy.props.BoolProperty(
        name="Hide Mirror",
        description="Hide mirror modifiers during selection",
        default=True
    )
    me_hide_solidify: bpy.props.BoolProperty(
        name="Hide Solidify",
        description="Hide solidify modifiers during selection",
        default=True
    )
    me_show_crosshair: bpy.props.BoolProperty(
        name="Show Crosshair",
        description="Show crosshair when wait_for_input is enabled",
        default=True
    )
    me_show_lasso_icon: bpy.props.BoolProperty(
        name="Show Lasso Cursor",
        description="Show lasso cursor icon when wait_for_input is enabled",
        default=True
    )

    ob_show_xray: bpy.props.BoolProperty(
        name="Show X-Ray",
        description="Enable x-ray shading during selection",
        default=True
    )
    ob_xray_toggle_key: bpy.props.EnumProperty(
        name="X-Ray Toggle Key",
        description="Toggle x-ray by holding this key",
        items=[('CTRL', "CTRL", ""),
               ('ALT', "ALT", ""),
               ('SHIFT', "SHIFT", ""),
               ('DISABLED', "DISABLED", "")
               ],
        default='DISABLED'
    )
    ob_xray_toggle_type: bpy.props.EnumProperty(
        name="Toggle X-Ray by Press or Hold",
        description="Toggle x-ray by holding or by pressing key",
        items=[('HOLD', "Holding", ""),
               ('PRESS', "Pressing", "")
               ],
        default='HOLD'
    )
    ob_show_crosshair: bpy.props.BoolProperty(
        name="Show Crosshair",
        description="Show crosshair when wait_for_input is enabled",
        default=True
    )
    ob_show_lasso_icon: bpy.props.BoolProperty(
        name="Show Lasso Cursor",
        description="Show lasso cursor icon when wait_for_input is enabled",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(self, "tabs", expand=True)
        box = col.box()

        if self.tabs == 'MESH_TOOLS':
            self.draw_mesh_tools(box)
        elif self.tabs == 'OBJECT_TOOLS':
            self.draw_object_tools(box)
        elif self.tabs == 'KEYMAP':
            self.draw_keymap(box)

    def draw_mesh_tools(self, box):
        box.label(text="Change shortcuts here or disable them by unchecking")

        col = box.column()
        kc = bpy.context.window_manager.keyconfigs.user
        km = kc.keymaps.get("Mesh")
        self.draw_keymap_items(kc, km, col, 3)

        flow = box.grid_flow(columns=2, row_major=True)

        flow.label(text="")
        flow.label(text="")

        flow.label(text="Start selection with enabled selection through")
        flow.prop(self, "me_select_through", text="Select Through", icon='MOD_WIREFRAME')

        flow.label(text="Toggle selection through by holding or by pressing this key during "
                        "selection")
        row = flow.row(align=True)
        sub = row.row(align=True)
        sub.active = self.me_select_through_toggle_key != 'DISABLED'
        sub.prop(self, "me_select_through_toggle_type", text="")
        row.prop(self, "me_select_through_toggle_key", text="")

        flow.label(text="")
        flow.label(text="")

        flow.label(text="Selection color when selection through is disabled")
        flow.prop(self, "me_default_color", text="")

        active = self.me_select_through or self.me_select_through_toggle_key != 'DISABLED'

        flow.label(text="Selection color when selection through is enabled")
        row = flow.row()
        row.active = active
        row.prop(self, "me_select_through_color", text="")

        flow.label(text="")
        flow.label(text="")

        flow.label(text="Show x-ray shading when selecting through")
        row = flow.row()
        row.active = active
        row.prop(self, "me_show_xray", text="Show X-Ray", icon='XRAY')

        flow.label(text="Select all edges touched by selection border")
        row = flow.row(align=True)
        row.active = active
        row.prop(self, "me_select_all_edges", text="Select All Edges", icon='EDGESEL')
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = \
            "select_all_edges"

        flow.label(text="Select all faces touched by selection border")
        row = flow.row(align=True)
        row.active = active
        row.prop(self, "me_select_all_faces", text="Select All Faces", icon='FACESEL')
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = \
            "select_all_faces"

        flow.label(text="")
        flow.label(text="")

        flow.label(text="Temporary hide this modifiers during selection")
        row = flow.row(align=True)
        row.prop(self, "me_hide_mirror", text="Mirror", icon='MOD_MIRROR')
        row.prop(self, "me_hide_solidify", text="Solidify", icon='MOD_SOLIDIFY')

        flow.label(text="")
        flow.label(text="")

        flow.label(text="Show crosshair of box tool or lasso icon of lasso tool on cursor")
        row = flow.row(align=True)
        row.prop(self, "me_show_crosshair", text="Show Crosshair", icon='RESTRICT_SELECT_OFF')
        row.prop(self, "me_show_lasso_icon", text="Show Lasso Icon", icon='RESTRICT_SELECT_OFF')
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = \
            "wait_for_input_cursor"

    def draw_object_tools(self, box):
        box.label(text="Change shortcuts here or disable them by unchecking")

        col = box.column()
        kc = bpy.context.window_manager.keyconfigs.user
        km = kc.keymaps.get("Object Mode")
        self.draw_keymap_items(kc, km, col, 3)

        flow = box.grid_flow(columns=2, row_major=True)

        flow.label(text="")
        flow.label(text="")

        flow.label(text="Start selection with enabled x-ray shading")
        flow.prop(self, "ob_show_xray", text="Show X-Ray", icon='XRAY')

        flow.label(text="Toggle x-ray shading by holding or by pressing this key during selection")
        row = flow.row(align=True)
        sub = row.row(align=True)
        sub.active = self.ob_xray_toggle_key != 'DISABLED'
        sub.prop(self, "ob_xray_toggle_type", text="")
        row.prop(self, "ob_xray_toggle_key", text="")

        flow.label(text="")
        flow.label(text="")

        flow.label(text="Show crosshair of box tool or lasso icon of lasso tool on cursor")
        row = flow.row(align=True)
        row.prop(self, "ob_show_crosshair", text="Show Crosshair", icon='RESTRICT_SELECT_OFF')
        row.prop(self, "ob_show_lasso_icon", text="Show Lasso Icon", icon='RESTRICT_SELECT_OFF')
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = \
            "wait_for_input_cursor"

    def draw_keymap(self, box):
        kc = bpy.context.window_manager.keyconfigs.user
        col = box.column()

        text = ("Change, disable or enable shortcuts here. To edit shortcut properties "
                "independently of global settings expand key item and check "
                "''Override Global Properties''")
        width = bpy.context.region.width
        wrapper = textwrap.TextWrapper(width=width / 6)  # 50 = maximum length
        wrapped_list = wrapper.wrap(text=text)

        for text in wrapped_list:
            row = col.row(align=True)
            row.label(text=text)

        box.label(text="Mesh Mode")
        col = box.column()
        km = kc.keymaps.get("Mesh")
        self.draw_keymap_items(kc, km, col)

        box.label(text="Object Mode ")
        col = box.column()
        km = kc.keymaps.get("Object Mode")
        self.draw_keymap_items(kc, km, col)

    @staticmethod
    def draw_keymap_items(kc, km, col, count=None):
        if count is None:
            count = len([km_tuple for km_tuple in addon_keymaps if km_tuple[0].name == km.name])
        # get only first keymap items from keymap, skipping user created keymap,
        # that goes after addon created keymap items
        kmis = [kmi for kmi in km.keymap_items if
                kmi.idname in {"mesh.select_box_xray", "object.select_box_xray",
                               "mesh.select_lasso_xray", "object.select_lasso_xray",
                               "mesh.select_circle_xray", "object.select_circle_xray",
                               "mesh.select_tools_xray_toggle_select_through"}][:count]
        for kmi in kmis:
            rna_keymap_ui.draw_kmi(['ADDON', 'USER', 'DEFAULT'], kc, km, kmi, col, 0)


classes = (
    XRAYSEL_preferences,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)

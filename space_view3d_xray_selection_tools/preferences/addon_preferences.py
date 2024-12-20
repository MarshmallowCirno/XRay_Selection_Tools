import bpy

from . import draw, properties
from .. import addon_info, tools
from ..operators import ot_keymap


# noinspection PyTypeChecker
class XRAYSELPreferences(bpy.types.AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = addon_info.get_addon_package()

    tabs: bpy.props.EnumProperty(
        name="Tabs",
        items=[
            ('MESH_TOOLS', "Mesh Tools", ""),
            ('OBJECT_TOOLS', "Object Tools", ""),
            ('KEYMAP', "Advanced Keymap", ""),
        ],
        default='MESH_TOOLS',
        options={'SKIP_SAVE'},
    )

    me_directional_box: bpy.props.BoolProperty(
        name="Directional Box Behavior",
        description="Configure behavior separately for dragging directions",
        default=False,
    )
    me_directional_lasso: bpy.props.BoolProperty(
        name="Directional Lasso Behavior",
        description="Configure behavior separately for dragging directions",
        default=False,
    )
    me_select_through: bpy.props.BoolProperty(
        name="Select Through",
        description="Select vertices, faces, and edges laying underneath",
        default=True,
    )
    me_select_through_toggle_key: bpy.props.EnumProperty(
        name="Selection Through Toggle Key",
        description="Toggle selection through with this key",
        items=[
            ('CTRL', "CTRL", ""),
            ('ALT', "ALT", ""),
            ('SHIFT', "SHIFT", ""),
            ('DISABLED', "DISABLED", ""),
        ],
        default='DISABLED',
    )
    me_select_through_toggle_type: bpy.props.EnumProperty(
        name="Toggle Selection Through by Press or Hold",
        description="Toggle selection through by holding or by pressing a key",
        items=[
            ('HOLD', "Holding", ""),
            ('PRESS', "Pressing", ""),
        ],
        default='HOLD',
    )
    me_default_color: bpy.props.FloatVectorProperty(
        name="Default Color",
        description="Color of the selection frame when not selecting through",
        subtype='COLOR',
        soft_min=0.0,
        soft_max=1.0,
        size=3,
        default=(1.0, 1.0, 1.0),
    )
    me_select_through_color: bpy.props.FloatVectorProperty(
        name="Select Through Color",
        description="Color of the selection frame when selecting through",
        subtype='COLOR',
        soft_min=0.0,
        soft_max=1.0,
        size=3,
        default=(1.0, 1.0, 1.0),
    )
    me_show_xray: bpy.props.BoolProperty(
        name="Show X-Ray",
        description="Enable X-Ray shading during selection",
        default=True,
    )
    me_select_all_edges: bpy.props.BoolProperty(
        name="Select All Edges",
        description=(
            "Include edges partially within the selection area, not just those fully enclosed. Works only "
            "in \"Select Through\" mode"
        ),
        default=False,
    )
    me_select_all_faces: bpy.props.BoolProperty(
        name="Select All Faces",
        description=(
            "Include faces partially within the selection borders, not just those whose centers are inside. "
            "Works only in \"Select Through\" mode"
        ),
        default=False,
    )
    me_select_backfacing: bpy.props.BoolProperty(
        name="Select Backfacing",
        description="Select elements with normals pointing away from the view. Works only in \"Select Through\" mode",
        default=True,
    )
    me_hide_mirror: bpy.props.BoolProperty(
        name="Hide Mirror",
        description="Temporarily hide mirror modifiers during selection",
        default=True,
    )
    me_hide_solidify: bpy.props.BoolProperty(
        name="Hide Solidify",
        description="Temporarily hide solidify modifiers during selection",
        default=True,
    )
    me_hide_gizmo: bpy.props.BoolProperty(
        name="Hide Gizmo",
        description="Temporarily hide the gizmo of the active tool during selection",
        default=False,
    )
    me_show_crosshair: bpy.props.BoolProperty(
        name="Show Crosshair",
        description="Display the crosshair when wait_for_input is enabled",
        default=True,
    )
    me_show_lasso_icon: bpy.props.BoolProperty(
        name="Show Lasso Cursor",
        description="Display the lasso cursor icon when wait_for_input is enabled",
        default=True,
    )
    me_tool_to_activate: bpy.props.EnumProperty(
        name="Activate automatically at startup",
        description="Set this tool as active in toolbar automatically when you start blender or load a save file",
        items=[
            ('NONE', "None", ""),
            ('BOX', "Select Box X-Ray", ""),
            ('CIRCLE', "Select Circle X-Ray", ""),
            ('LASSO', "Select Lasso X-Ray", ""),
        ],
        default='NONE',
    )
    me_group_with_builtins: bpy.props.BoolProperty(
        name="Directional Box Behavior",
        description="Set tool behavior based on drag direction",
        default=True,
        update=tools.reload_tools,
    )

    ob_show_xray: bpy.props.BoolProperty(
        name="Show X-Ray",
        description="Enable X-Ray shading during selection",
        default=True,
    )
    ob_xray_toggle_key: bpy.props.EnumProperty(
        name="X-Ray Toggle Key",
        description="Toggle X-Ray with this key",
        items=[
            ('CTRL', "CTRL", ""),
            ('ALT', "ALT", ""),
            ('SHIFT', "SHIFT", ""),
            ('DISABLED', "DISABLED", ""),
        ],
        default='DISABLED',
    )
    ob_xray_toggle_type: bpy.props.EnumProperty(
        name="Toggle X-Ray by Press or Hold",
        description="Toggle X-Ray by holding or by pressing a key",
        items=[
            ('HOLD', "Holding", ""),
            ('PRESS', "Pressing", ""),
        ],
        default='HOLD',
    )
    ob_hide_gizmo: bpy.props.BoolProperty(
        name="Hide Gizmo",
        description="Hide the gizmo of the active tool during selection",
        default=False,
    )
    ob_show_crosshair: bpy.props.BoolProperty(
        name="Show Crosshair",
        description="Display the crosshair when wait_for_input is enabled",
        default=True,
    )
    ob_show_lasso_icon: bpy.props.BoolProperty(
        name="Show Lasso Cursor",
        description="Display the lasso cursor icon when wait_for_input is enabled",
        default=True,
    )
    ob_box_select_behavior: bpy.props.EnumProperty(
        name="Box Select Behavior",
        description="Selection behavior",
        items=[
            (
                'ORIGIN',
                "Origin",
                "Select objects by origins",
                'DOT',
                1,
            ),
            (
                'CONTAIN',
                "Contain",
                "Select only the objects fully contained in box",
                'STICKY_UVS_LOC',
                2,
            ),
            (
                'OVERLAP',
                "Overlap (Default)",
                "Select objects overlapping box",
                'SELECT_SUBTRACT',
                3,
            ),
            (
                'DIRECTIONAL',
                "Directional",
                "Dragging left to right select contained, right to left select overlapped",
                'UV_SYNC_SELECT',
                4,
            ),
            (
                'DIRECTIONAL_REVERSED',
                "Directional Reversed",
                "Dragging left to right select overlapped, right to left select contained",
                'UV_SYNC_SELECT',
                5,
            ),
        ],
        default='OVERLAP',
    )
    ob_circle_select_behavior: bpy.props.EnumProperty(
        name="Circle Select Behavior",
        description="Selection behavior",
        items=[
            (
                'ORIGIN',
                "Origin (Default)",
                "Select objects by origins",
                'DOT',
                1,
            ),
            (
                'CONTAIN',
                "Contain",
                "Select only the objects fully contained in circle",
                'STICKY_UVS_LOC',
                2,
            ),
            (
                'OVERLAP',
                "Overlap",
                "Select objects overlapping circle",
                'SELECT_SUBTRACT',
                3,
            ),
        ],
        default='ORIGIN',
    )
    ob_lasso_select_behavior: bpy.props.EnumProperty(
        name="Lasso Select Behavior",
        description="Selection behavior",
        items=[
            (
                'ORIGIN',
                "Origin (Default)",
                "Select objects by origins",
                'DOT',
                1,
            ),
            (
                'CONTAIN',
                "Contain",
                "Select only the objects fully contained in lasso",
                'STICKY_UVS_LOC',
                2,
            ),
            (
                'OVERLAP',
                "Overlap",
                "Select objects overlapping lasso",
                'SELECT_SUBTRACT',
                3,
            ),
            (
                'DIRECTIONAL',
                "Directional",
                "Dragging left to right select contained, right to left select overlapped",
                'UV_SYNC_SELECT',
                4,
            ),
            (
                'DIRECTIONAL_REVERSED',
                "Directional Reversed",
                "Dragging left to right select overlapped, right to left select contained",
                'UV_SYNC_SELECT',
                5,
            ),
        ],
        default='ORIGIN',
    )
    ob_tool_to_activate: bpy.props.EnumProperty(
        name="Activate automatically at startup",
        description="Set this tool as active in toolbar automatically when you start blender or load a save file",
        items=[
            ('NONE', "None", ""),
            ('BOX', "Select Box X-Ray", ""),
            ('CIRCLE', "Select Circle X-Ray", ""),
            ('LASSO', "Select Lasso X-Ray", ""),
        ],
        default='NONE',
    )
    ob_group_with_builtins: bpy.props.BoolProperty(
        name="Directional Box Behavior",
        description="Set tool behavior based on drag direction",
        default=True,
        update=tools.reload_tools,
    )

    enable_me_keyboard_keymap: bpy.props.BoolProperty(
        name="Mesh Mode Keyboard Shortcuts",
        description="Enable to add shortcuts to the Blender keymap, or disable to remove them",
        update=ot_keymap.toggle_me_keyboard_keymap,
        default=True,
    )
    enable_me_mouse_keymap: bpy.props.BoolProperty(
        name="Mesh Mode Mouse Shortcuts",
        description="Enable to add shortcuts to the Blender keymap, or disable to remove them",
        update=ot_keymap.toggle_me_mouse_keymap,
        default=False,
    )
    enable_ob_keyboard_keymap: bpy.props.BoolProperty(
        name="Object Mode Keyboard Shortcuts",
        description="Enable to add shortcuts to the Blender keymap, or disable to remove them",
        update=ot_keymap.toggle_ob_keyboard_keymap,
        default=True,
    )
    enable_ob_mouse_keymap: bpy.props.BoolProperty(
        name="Object Mode Mouse Shortcuts",
        description="Enable to add shortcuts to the Blender keymap, or disable to remove them",
        update=ot_keymap.toggle_ob_mouse_keymap,
        default=False,
    )
    enable_toggles_keymap: bpy.props.BoolProperty(
        name="Preferences Toggles Shortcuts",
        description="Enable to add shortcuts to the Blender keymap, or disable to remove them",
        update=ot_keymap.toggle_toggles_keymap,
        default=False,
    )

    keymaps_of_tools: bpy.props.CollectionProperty(
        type=properties.XRAYSELToolKeymapPG,
        name="Keymaps of Tools",
    )
    me_direction_properties: bpy.props.CollectionProperty(
        type=properties.XRAYSELToolMeDirectionProps,
        name="Mesh Direction Props",
    )

    select_mouse: bpy.props.EnumProperty(
        description="Last known value of the property, as keyconfig.preferences is unavailable at Blender startup",
        items=[
            ('LEFT', "", ""),
            ('RIGHT', "", ""),
        ],
        default='LEFT',
    )

    rmb_action: bpy.props.EnumProperty(
        description="Last known value of the property, as keyconfig.preferences is unavailable at Blender startup",
        items=[
            ('TWEAK', "", ""),
            ('FALLBACK_TOOL', "", ""),
        ],
        default='TWEAK',
    )

    tool_keymap_tabs: bpy.props.EnumProperty(
        name="Tool Selection Modifier Keys",
        items=[
            ('BOX', "Box Tool", ""),
            ('CIRCLE', "Circle Tool", ""),
            ('LASSO', "Lasso Tool", ""),
        ],
        default='BOX',
        options={'SKIP_SAVE'},
    )

    def draw(self, _):
        layout = self.layout

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(self, "tabs", expand=True)
        box = col.box()

        if self.tabs == 'MESH_TOOLS':
            draw.draw_mesh_tools_preferences(self, box)
        elif self.tabs == 'OBJECT_TOOLS':
            draw.draw_object_tools_preferences(self, box)
        elif self.tabs == 'KEYMAP':
            draw.draw_keymaps(self, box)

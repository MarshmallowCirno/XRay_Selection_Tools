import bpy
import rna_keymap_ui

from .addon_info import get_preferences
from .operators.ot_keymap import (
    me_keyboard_keymap,
    me_mouse_keymap,
    ob_keyboard_keymap,
    ob_mouse_keymap,
    toggle_me_keyboard_keymap,
    toggle_me_mouse_keymap,
    toggle_ob_keyboard_keymap,
    toggle_ob_mouse_keymap,
    toggle_toggles_keymap,
    toggles_keymap,
)
from .tools import reload_tools, update_keymaps_of_tools
from .tools.tools_keymap import populate_preferences_keymaps_of_tools


class XRAYSELToolKmiPG(bpy.types.PropertyGroup):
    # name = StringProperty() -> Instantiated by default
    description: bpy.props.StringProperty(name="Description")
    icon: bpy.props.StringProperty(name="Icon")
    active: bpy.props.BoolProperty(
        name="Active",
        description="Enable or disable selection mode",
        update=update_keymaps_of_tools,
        default=True,
    )
    shift: bpy.props.BoolProperty(
        name="Shift",
        description="Shift key is pressed",
        update=update_keymaps_of_tools,
        default=False,
    )
    ctrl: bpy.props.BoolProperty(
        name="Ctrl",
        description="Ctrl key is pressed",
        update=update_keymaps_of_tools,
        default=False,
    )
    alt: bpy.props.BoolProperty(
        name="Alt",
        description="Alt key is pressed",
        update=update_keymaps_of_tools,
        default=False,
    )


class XRAYSELToolKeymapPG(bpy.types.PropertyGroup):
    # name = StringProperty() -> Instantiated by default
    kmis: bpy.props.CollectionProperty(name="KMIS", type=XRAYSELToolKmiPG)


class XRAYSELToolMeDirectionProps(bpy.types.PropertyGroup):
    # name = StringProperty() -> Instantiated by default
    select_through: bpy.props.BoolProperty(
        name="Select Through",
        description="Select vertices, faces, and edges laying underneath",
        default=True,
    )
    default_color: bpy.props.FloatVectorProperty(
        name="Default Color",
        description="Color of the selection frame when selecting through",
        subtype='COLOR',
        soft_min=0.0,
        soft_max=1.0,
        size=3,
        default=(1.0, 1.0, 1.0),
    )
    select_through_color: bpy.props.FloatVectorProperty(
        name="Select Through Color",
        description="Color of the selection frame when not selecting through",
        subtype='COLOR',
        soft_min=0.0,
        soft_max=1.0,
        size=3,
        default=(1.0, 1.0, 1.0),
    )
    show_xray: bpy.props.BoolProperty(
        name="Show X-Ray",
        description="Enable X-Ray shading during selection",
        default=True,
    )
    select_all_edges: bpy.props.BoolProperty(
        name="Select All Edges",
        description=(
            "Include edges partially within the selection area, not just those fully enclosed. Works only "
            "in \"Select Through\" mode"
        ),
        default=False,
    )
    select_all_faces: bpy.props.BoolProperty(
        name="Select All Faces",
        description=(
            "Include faces partially within the selection borders, not just those whose centers are inside. "
            "Works only in \"Select Through\" mode"
        ),
        default=False,
    )
    select_backfacing: bpy.props.BoolProperty(
        name="Select Backfacing",
        description="Select elements with normals pointing away from the view. Works only in \"Select Through\" mode",
        default=True,
    )


# noinspection PyTypeChecker
class XRAYSELPreferences(bpy.types.AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

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
        update=reload_tools,
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
        update=reload_tools,
    )

    enable_me_keyboard_keymap: bpy.props.BoolProperty(
        name="Mesh Mode Keyboard Shortcuts",
        description="Enable to add shortcuts to the Blender keymap, or disable to remove them",
        update=toggle_me_keyboard_keymap,
        default=True,
    )
    enable_me_mouse_keymap: bpy.props.BoolProperty(
        name="Mesh Mode Mouse Shortcuts",
        description="Enable to add shortcuts to the Blender keymap, or disable to remove them",
        update=toggle_me_mouse_keymap,
        default=False,
    )
    enable_ob_keyboard_keymap: bpy.props.BoolProperty(
        name="Object Mode Keyboard Shortcuts",
        description="Enable to add shortcuts to the Blender keymap, or disable to remove them",
        update=toggle_ob_keyboard_keymap,
        default=True,
    )
    enable_ob_mouse_keymap: bpy.props.BoolProperty(
        name="Object Mode Mouse Shortcuts",
        description="Enable to add shortcuts to the Blender keymap, or disable to remove them",
        update=toggle_ob_mouse_keymap,
        default=False,
    )
    enable_toggles_keymap: bpy.props.BoolProperty(
        name="Preferences Toggles Shortcuts",
        description="Enable to add shortcuts to the Blender keymap, or disable to remove them",
        update=toggle_toggles_keymap,
        default=False,
    )

    keymaps_of_tools: bpy.props.CollectionProperty(
        type=XRAYSELToolKeymapPG,
        name="Keymaps of Tools",
    )
    me_direction_properties: bpy.props.CollectionProperty(
        type=XRAYSELToolMeDirectionProps,
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
            self.draw_mesh_tools_preferences(box)
        elif self.tabs == 'OBJECT_TOOLS':
            self.draw_object_tools_preferences(box)
        elif self.tabs == 'KEYMAP':
            self.draw_adv_keymap(box)

    @staticmethod
    def draw_flow_vertical_separator(flow):
        row = flow.row()
        row.scale_y = 0.7
        row.label(text="")
        row = flow.row()
        row.scale_y = 0.7
        row.label(text="")

    def draw_mesh_tools_preferences(self, box):
        """Mesh Tools tab."""
        use_directional_props = self.me_directional_box | self.me_directional_lasso

        dir_tools = []
        def_tools = ["Circle"]
        if self.me_directional_box:
            dir_tools.append("Box")
        else:
            def_tools.append("Box")
        if self.me_directional_lasso:
            dir_tools.append("Lasso")
        else:
            def_tools.append("Lasso")

        rtl_props = self.me_direction_properties["RIGHT_TO_LEFT"]
        ltr_props = self.me_direction_properties["LEFT_TO_RIGHT"]

        rtl_st_available = rtl_props.select_through or self.me_select_through_toggle_key != 'DISABLED'
        ltr_st_available = ltr_props.select_through or self.me_select_through_toggle_key != 'DISABLED'
        def_st_available = self.me_select_through or self.me_select_through_toggle_key != 'DISABLED'

        # Keymap
        if self.enable_me_keyboard_keymap:
            box.label(text="Modify shortcuts here or disable them by unchecking")
            col = box.column()
            self.draw_keymap_items(col, "Mesh", me_keyboard_keymap, None, False)
            box.separator(factor=1.7)

        flow = box.grid_flow(columns=2, row_major=True, align=True)

        # Select through
        if not use_directional_props:
            flow.label(text="Start selection with \"Select Through\" mode enabled")
            flow.prop(self, "me_select_through", text="Select Through", icon='MOD_WIREFRAME')

        # Select through toggle
        flow.label(text="Toggle \"Select Through\" mode while selecting using a following key")
        split = flow.split(align=True)
        sub = split.row(align=True)
        sub.active = self.me_select_through_toggle_key != 'DISABLED'
        sub.prop(self, "me_select_through_toggle_type", text="")
        split.prop(self, "me_select_through_toggle_key", text="")

        if use_directional_props:
            self.draw_flow_vertical_separator(flow)
            # Labels
            flow.label(text="Tool")
            split = flow.split(align=True)
            row = split.row()
            row.label(text="", icon='BLANK1')
            sub = row.row()
            sub.alignment = 'CENTER'
            sub.label(text=" and ".join(dir_tools))
            row = split.row()
            row.label(text="", icon='BLANK1')
            sub = row.row()
            sub.alignment = 'CENTER'
            sub.label(text=" and ".join(dir_tools))
            row = split.row()
            row.label(text="", icon='BLANK1')
            sub = row.row()
            sub.alignment = 'CENTER'
            sub.label(text=" and ".join(def_tools))

            # Directions
            flow.label(text="Drag direction")
            split = flow.split(align=True)
            row = split.row()
            row.label(text="", icon='BACK')
            sub = row.row()
            sub.alignment = 'CENTER'
            sub.label(text="Right to Left")
            row = split.row()
            row.label(text="", icon='FORWARD')
            sub = row.row()
            sub.alignment = 'CENTER'
            sub.label(text="Left to Right")
            row = split.row()
            row.label(text="", icon='ARROW_LEFTRIGHT')
            sub = row.row()
            sub.alignment = 'CENTER'
            sub.label(text="Any")

            # Select through
            flow.label(text="Start selection with \"Select Through\" mode enabled")
            split = flow.split(align=True)
            split.prop(rtl_props, "select_through", text="Select Through", icon='MOD_WIREFRAME')
            split.prop(ltr_props, "select_through", text="Select Through", icon='MOD_WIREFRAME')
            split.prop(self, "me_select_through", text="Select Through", icon='MOD_WIREFRAME')

            # Color
            flow.label(text="Color of the selection frame when not selecting through")
            split = flow.split(align=True)
            split.prop(rtl_props, "default_color", text="")
            split.prop(ltr_props, "default_color", text="")
            split.prop(self, "me_default_color", text="")
            flow.label(text="Color of the selection frame when selecting through")
            split = flow.split(align=True)
            split.prop(rtl_props, "select_through_color", text="")
            split.prop(ltr_props, "select_through_color", text="")
            split.prop(self, "me_select_through_color", text="")

            # Show x-ray
            flow.label(text="Enable X-Ray shading during selection")
            split = flow.split(align=True)
            row = split.row(align=True)
            row.active = rtl_st_available
            row.prop(rtl_props, "show_xray", text="Show X-Ray", icon='XRAY')
            row = split.row(align=True)
            row.active = ltr_st_available
            row.prop(ltr_props, "show_xray", text="Show X-Ray", icon='XRAY')
            row = split.row(align=True)
            row.active = def_st_available
            row.prop(self, "me_show_xray", text="Show X-Ray", icon='XRAY')

            # All edges
            row = flow.row(align=True)
            row.label(text="Select all edges intersecting the selection region")
            row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "me_select_all_edges"
            split = flow.split(align=True)
            row = split.row(align=True)
            row.active = rtl_st_available
            row.prop(rtl_props, "select_all_edges", text="Select All Edges", icon='EDGESEL')
            row = split.row(align=True)
            row.active = ltr_st_available
            row.prop(ltr_props, "select_all_edges", text="Select All Edges", icon='EDGESEL')
            row = split.row(align=True)
            row.active = def_st_available
            row.prop(self, "me_select_all_edges", text="Select All Edges", icon='EDGESEL')

            # All faces
            row = flow.row(align=True)
            row.label(text="Select all faces intersecting the selection region")
            row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "me_select_all_faces"
            split = flow.split(align=True)
            row = split.row(align=True)
            row.active = rtl_st_available
            row.prop(rtl_props, "select_all_faces", text="Select All Faces", icon='FACESEL')
            row = split.row(align=True)
            row.active = ltr_st_available
            row.prop(ltr_props, "select_all_faces", text="Select All Faces", icon='FACESEL')
            row = split.row(align=True)
            row.active = def_st_available
            row.prop(self, "me_select_all_faces", text="Select All Faces", icon='FACESEL')

            # Backfacing
            row = flow.row(align=True)
            row.label(text="Select elements with normals pointing away from the view")
            row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "me_select_backfacing"
            split = flow.split(align=True)
            row = split.row(align=True)
            row.active = rtl_st_available
            row.prop(rtl_props, "select_backfacing", text="Select Backfacing", icon='NORMALS_FACE')
            row = split.row(align=True)
            row.active = ltr_st_available
            row.prop(ltr_props, "select_backfacing", text="Select Backfacing", icon='NORMALS_FACE')
            row = split.row(align=True)
            row.active = def_st_available
            row.prop(self, "me_select_backfacing", text="Select Backfacing", icon='NORMALS_FACE')
        else:
            # Color
            self.draw_flow_vertical_separator(flow)
            flow.label(text="Color of the selection frame when not selecting through")
            flow.prop(self, "me_default_color", text="")
            flow.label(text="Color of the selection frame when selecting through")
            flow.prop(self, "me_select_through_color", text="")

            # Show x-ray
            self.draw_flow_vertical_separator(flow)
            flow.label(text="Enable X-Ray shading during selection")
            row = flow.row()
            row.active = def_st_available
            row.prop(self, "me_show_xray", text="Show X-Ray", icon='XRAY')

            # All edges and faces
            self.draw_flow_vertical_separator(flow)
            flow.label(text="Select all edges intersecting the selection region")
            row = flow.row(align=True)
            row.active = def_st_available
            row.prop(self, "me_select_all_edges", text="Select All Edges", icon='EDGESEL')
            row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "me_select_all_edges"

            flow.label(text="Select all faces intersecting the selection region")
            row = flow.row(align=True)
            row.active = def_st_available
            row.prop(self, "me_select_all_faces", text="Select All Faces", icon='FACESEL')
            row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "me_select_all_faces"

            flow.label(text="Select elements with normals pointing away from the view")
            row = flow.row(align=True)
            row.active = def_st_available
            row.prop(self, "me_select_backfacing", text="Select Backfacing", icon='NORMALS_FACE')
            row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "me_select_backfacing"

        # Directional toggles
        self.draw_flow_vertical_separator(flow)
        flow.label(text="Set tool behavior based on drag direction")
        split = flow.split(align=True)
        split.prop(self, "me_directional_box", text="Directional Box", icon='UV_SYNC_SELECT')
        row = split.row(align=True)
        row.prop(self, "me_directional_lasso", text="Directional Lasso", icon='UV_SYNC_SELECT')
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "me_drag_direction"

        # Modifiers
        self.draw_flow_vertical_separator(flow)
        flow.label(text="Temporarily hide these modifiers during selection")
        split = flow.split(align=True)
        if use_directional_props:
            split.active = rtl_st_available or ltr_st_available or def_st_available
        else:
            split.active = def_st_available
        split.prop(self, "me_hide_mirror", text="Hide Mirror", icon='MOD_MIRROR')
        row = split.row(align=True)
        row.prop(self, "me_hide_solidify", text="Hide Solidify", icon='MOD_SOLIDIFY')
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "me_hide_modifiers"

        # Gizmo
        self.draw_flow_vertical_separator(flow)
        flow.label(text="Temporarily hide the gizmo of the active tool")
        row = flow.row(align=True)
        row.prop(self, "me_hide_gizmo", text="Hide Gizmo", icon='GIZMO')
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "hide_gizmo"

        # Icon
        self.draw_flow_vertical_separator(flow)
        flow.label(text="Display the box tool crosshair or lasso tool icon")
        split = flow.split(align=True)
        split.prop(self, "me_show_crosshair", text="Show Crosshair", icon='RESTRICT_SELECT_OFF')
        row = split.row(align=True)
        row.prop(self, "me_show_lasso_icon", text="Show Lasso Icon", icon='RESTRICT_SELECT_OFF')
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "wait_for_input_cursor"

        # Startup
        self.draw_flow_vertical_separator(flow)
        flow.label(text="Automatically activate following tool at startup")
        flow.prop(self, "me_tool_to_activate", text="")

        # Group with builtin tools
        self.draw_flow_vertical_separator(flow)
        flow.label(text="Group with built-in selection tools in the toolbar")
        row = flow.row(align=True)
        row.prop(self, "me_group_with_builtins", text="Group with Builtins", icon='GROUP')
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "group_with_builtins"

    def draw_object_tools_preferences(self, box):
        """Object Tools tab."""

        # Keymap
        if self.enable_ob_keyboard_keymap:
            box.label(text="Modify shortcuts here or disable them by unchecking")
            col = box.column()
            self.draw_keymap_items(col, "Object Mode", ob_keyboard_keymap, None, False)
            box.separator(factor=1.7)

        flow = box.grid_flow(columns=2, row_major=True, align=True)

        # Select through
        flow.label(text="Start selection with X-Ray shading enabled")
        flow.prop(self, "ob_show_xray", text="Show X-Ray", icon='XRAY')

        # Select toggle
        flow.label(text="Toggle X-Ray shading while selecting using a following key")
        split = flow.split(align=True)
        sub = split.row(align=True)
        sub.active = self.ob_xray_toggle_key != 'DISABLED'
        sub.prop(self, "ob_xray_toggle_type", text="")
        split.prop(self, "ob_xray_toggle_key", text="")

        # Behavior
        self.draw_flow_vertical_separator(flow)
        flow.label(text="Box tool behavior")
        row = flow.row(align=True)
        row.prop(self, "ob_box_select_behavior", text="")
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "ob_selection_behavior"
        flow.label(text="Circle tool behavior")
        row = flow.row(align=True)
        row.prop(self, "ob_circle_select_behavior", text="")
        row.label(text="", icon='BLANK1')
        flow.label(text="Lasso tool behavior")
        row = flow.row(align=True)
        row.prop(self, "ob_lasso_select_behavior", text="")
        row.label(text="", icon='BLANK1')

        # Gizmo
        self.draw_flow_vertical_separator(flow)
        flow.label(text="Temporarily hide the gizmo of the active tool")
        row = flow.row(align=True)
        row.prop(self, "ob_hide_gizmo", text="Hide Gizmo", icon='GIZMO')
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "hide_gizmo"

        # Icon
        self.draw_flow_vertical_separator(flow)
        flow.label(text="Display the box tool crosshair or lasso tool icon")
        split = flow.split(align=True)
        split.prop(self, "ob_show_crosshair", text="Show Crosshair", icon='RESTRICT_SELECT_OFF')
        row = split.row(align=True)
        row.prop(self, "ob_show_lasso_icon", text="Show Lasso Icon", icon='RESTRICT_SELECT_OFF')
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "wait_for_input_cursor"

        # Startup
        self.draw_flow_vertical_separator(flow)
        flow.label(text="Automatically activate following tool at startup")
        flow.prop(self, "ob_tool_to_activate", text="")

        # Group with builtin tools
        self.draw_flow_vertical_separator(flow)
        flow.label(text="Group with built-in selection tools in the toolbar")
        row = flow.row(align=True)
        row.prop(self, "ob_group_with_builtins", text="Group with Builtins", icon='GROUP')
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "group_with_builtins"

    def draw_adv_keymap(self, box):
        """Advanced Keymap tab."""

        # Object and Mesh Mode Keymap
        col = box.column()
        row = col.row(align=True)
        row.label(text="Shortcuts for activating tools and modifying preferences")
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "tool_keymaps"

        col = box.column()

        km_col = col.column(align=True)
        icon = 'CHECKBOX_HLT' if self.enable_me_keyboard_keymap else 'CHECKBOX_DEHLT'
        km_col.prop(self, "enable_me_keyboard_keymap", text="Mesh Mode Tools: Keyboard Shortcuts", icon=icon)
        if self.enable_me_keyboard_keymap:
            sub_box = km_col.box()
            kmi_col = sub_box.column(align=True)
            self.draw_keymap_items(kmi_col, "Mesh", me_keyboard_keymap, {'KEYBOARD'}, True)

        km_col = col.column(align=True)
        icon = 'CHECKBOX_HLT' if self.enable_ob_keyboard_keymap else 'CHECKBOX_DEHLT'
        km_col.prop(self, "enable_ob_keyboard_keymap", text="Object Mode Tools: Keyboard Shortcuts", icon=icon)
        if self.enable_ob_keyboard_keymap:
            sub_box = km_col.box()
            kmi_col = sub_box.column(align=True)
            self.draw_keymap_items(kmi_col, "Object Mode", ob_keyboard_keymap, {'KEYBOARD'}, True)

        km_col = col.column(align=True)
        icon = 'CHECKBOX_HLT' if self.enable_me_mouse_keymap else 'CHECKBOX_DEHLT'
        km_col.prop(self, "enable_me_mouse_keymap", text="Mesh Mode Tools: Mouse Shortcuts", icon=icon)
        if self.enable_me_mouse_keymap:
            sub_box = km_col.box()
            kmi_col = sub_box.column(align=True)
            self.draw_keymap_items(kmi_col, "Mesh", me_mouse_keymap, {'MOUSE', 'TWEAK'}, True)

        km_col = col.column(align=True)
        icon = 'CHECKBOX_HLT' if self.enable_ob_mouse_keymap else 'CHECKBOX_DEHLT'
        km_col.prop(self, "enable_ob_mouse_keymap", text="Object Mode Tools: Mouse Shortcuts", icon=icon)
        if self.enable_ob_mouse_keymap:
            sub = km_col.box()
            kmi_col = sub.column(align=True)
            self.draw_keymap_items(kmi_col, "Object Mode", ob_mouse_keymap, {'MOUSE', 'TWEAK'}, True)

        km_col = col.column(align=True)
        icon = 'CHECKBOX_HLT' if self.enable_toggles_keymap else 'CHECKBOX_DEHLT'
        km_col.prop(self, "enable_toggles_keymap", text="Preferences Toggle Shortcuts", icon=icon)
        if self.enable_toggles_keymap:
            sub_box = km_col.box()
            kmi_col = sub_box.column(align=True)
            self.draw_keymap_items(kmi_col, "Mesh", toggles_keymap, {'MOUSE', 'TWEAK', 'KEYBOARD'}, True)

        # Tool Selection Mode Keymap
        box.separator()
        row = box.row(align=True)
        row.label(text="Shortcuts for selection modes of toolbar tools")
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "tool_selection_mode_keymaps"

        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(self, "tool_keymap_tabs", expand=True)

        tool = self.tool_keymap_tabs
        keymap = self.keymaps_of_tools[tool]
        kmis = keymap.kmis
        for mode in kmis.keys():
            row = col.row(align=True)
            description = kmis[mode].description
            icon = kmis[mode].icon
            row.prop(kmis[mode], "active", text=description, icon=icon)

            sub = row.row(align=True)
            sub.active = kmis[mode].active
            sub.prop(kmis[mode], "shift", text="Shift", toggle=True)
            sub.prop(kmis[mode], "ctrl", text="Ctrl", toggle=True)
            sub.prop(kmis[mode], "alt", text="Alt", toggle=True)

    @staticmethod
    def draw_keymap_items(col, km_name, keymap, map_type=None, allow_remove=False):
        kc = bpy.context.window_manager.keyconfigs.user
        km = kc.keymaps.get(km_name)
        kmi_idnames = [km_tuple[1].idname for km_tuple in keymap]
        if allow_remove:
            col.context_pointer_set("keymap", km)

        if map_type is None:
            kmis = [kmi for kmi in km.keymap_items if kmi.idname in kmi_idnames and kmi.map_type]
        else:
            kmis = [kmi for kmi in km.keymap_items if kmi.idname in kmi_idnames and kmi.map_type in map_type]

        for kmi in kmis:
            rna_keymap_ui.draw_kmi(['ADDON', 'USER', 'DEFAULT'], kc, km, kmi, col, 0)


def populate_preferences_direction_properties():
    left = get_preferences().me_direction_properties.add()
    left.name = "RIGHT_TO_LEFT"
    left = get_preferences().me_direction_properties.add()
    left.name = "LEFT_TO_RIGHT"


classes = (XRAYSELToolMeDirectionProps, XRAYSELToolKmiPG, XRAYSELToolKeymapPG, XRAYSELPreferences)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    populate_preferences_keymaps_of_tools()
    populate_preferences_direction_properties()


def unregister():
    get_preferences().me_direction_properties.clear()
    get_preferences().keymaps_of_tools.clear()

    from bpy.utils import unregister_class

    for cls in classes:
        unregister_class(cls)

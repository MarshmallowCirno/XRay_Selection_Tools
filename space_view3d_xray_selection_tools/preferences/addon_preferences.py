from typing import TYPE_CHECKING, Literal

import bpy

from .. import addon_info
from . import draw, properties


class XRAYSELPreferences(bpy.types.AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = addon_info.get_addon_package()

    if TYPE_CHECKING:
        mesh_tools: properties.XRAYSELMeshToolsPreferencesPG
        object_tools: properties.XRAYSELObjectToolsPreferencesPG
        keymaps: properties.XRAYSELKeymapsPreferencesPG

        active_tab: Literal['MESH_TOOLS', 'OBJECT_TOOLS', 'KEYMAP']
        select_mouse: Literal['LEFT', 'RIGHT']
        rmb_action: Literal['TWEAK', 'FALLBACK_TOOL']
    else:
        mesh_tools: bpy.props.PointerProperty(type=properties.XRAYSELMeshToolsPreferencesPG)
        object_tools: bpy.props.PointerProperty(type=properties.XRAYSELObjectToolsPreferencesPG)
        keymaps: bpy.props.PointerProperty(type=properties.XRAYSELKeymapsPreferencesPG)

        active_tab: bpy.props.EnumProperty(
            name="Tabs",
            items=[
                ('MESH_TOOLS', "Mesh Tools", ""),
                ('OBJECT_TOOLS', "Object Tools", ""),
                ('KEYMAP', "Keymaps", ""),
            ],
            default='MESH_TOOLS',
            options={'SKIP_SAVE'},
        )

        select_mouse: bpy.props.EnumProperty(
            description="Last known value of the property, since keyconfig.preferences is unavailable at Blender startup",
            items=[
                ('LEFT', "", ""),
                ('RIGHT', "", ""),
            ],
            default='LEFT',
        )

        rmb_action: bpy.props.EnumProperty(
            description="Last known value of the property, since keyconfig.preferences is unavailable at Blender startup",
            items=[
                ('TWEAK', "", ""),
                ('FALLBACK_TOOL', "", ""),
            ],
            default='TWEAK',
        )

    def draw(self, _context: bpy.types.Context):
        col = self.layout.column(align=True)
        row = col.row(align=True)
        row.prop(self, "active_tab", expand=True)
        box = col.box()

        match self.active_tab:
            case 'MESH_TOOLS':
                draw.draw_mesh_tools_preferences(self, box)
            case 'OBJECT_TOOLS':
                draw.draw_object_tools_preferences(self, box)
            case 'KEYMAP':
                draw.draw_keymaps(self, box)

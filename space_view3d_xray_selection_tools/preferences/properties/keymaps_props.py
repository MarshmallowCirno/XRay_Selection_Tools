import bpy

from ... import tools


class XRAYSELToolKmiPG(bpy.types.PropertyGroup):
    # name = StringProperty() -> Instantiated by default
    description: bpy.props.StringProperty(name="Description")
    icon: bpy.props.StringProperty(name="Icon")
    active: bpy.props.BoolProperty(
        name="Active",
        description="Enable or disable selection mode",
        update=tools.update_keymaps_of_tools,
        default=True,
    )
    shift: bpy.props.BoolProperty(
        name="Shift",
        description="Shift key is pressed",
        update=tools.update_keymaps_of_tools,
        default=False,
    )
    ctrl: bpy.props.BoolProperty(
        name="Ctrl",
        description="Ctrl key is pressed",
        update=tools.update_keymaps_of_tools,
        default=False,
    )
    alt: bpy.props.BoolProperty(
        name="Alt",
        description="Alt key is pressed",
        update=tools.update_keymaps_of_tools,
        default=False,
    )


class XRAYSELToolKeymapPG(bpy.types.PropertyGroup):
    # name = StringProperty() -> Instantiated by default
    kmis: bpy.props.CollectionProperty(name="KMIS", type=XRAYSELToolKmiPG)

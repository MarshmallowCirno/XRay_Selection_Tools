import bpy


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

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
    "name": "X-Ray Selection Tools",
    "author": "MarshmallowCirno",
    "version": (3, 0, 0),
    "blender": (2, 83, 0),
    "location": "Toolbar > Selection Tools",
    "description": "Box, lasso and circle selection tools with x-ray",
    "warning": "",
    "category": "3D View",
    "doc_url": "https://gumroad.com/l/DaLdj",
    "tracker_url": "https://blenderartists.org/t/box-select-x-ray/1212316/1",
}


reloadable_modules = (
    "intersect",
    "mesh_modal",
    "object_modal",
    "mesh_op_box",
    "mesh_op_circle",
    "mesh_op_lasso",
    "object_op_box",
    "object_op_circle",
    "object_op_lasso",
    "global_op",
    "help",
    "keymaps",
    "legacy_register",
    "tools",
    "tools_dummy",
    "ui"
)


# when bpy is already in local, we know this is not the initial import...
if "bpy" in locals():
    # ...so we need to reload our submodule(s) using importlib
    import importlib
    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])
else:
    from .functions import intersect, mesh_modal, object_modal
    from .mesh import mesh_op_box, mesh_op_circle, mesh_op_lasso
    from .object import object_op_box, object_op_circle, object_op_lasso
    from . import global_op, help, keymaps, tools, tools_dummy, ui


import bpy


def register():
    mesh_op_box.register()
    mesh_op_circle.register()
    mesh_op_lasso.register()
    object_op_box.register()
    object_op_circle.register()
    object_op_lasso.register()
    global_op.register()
    help.register()
    ui.register()
    tools.register()
    tools_dummy.register()
    keymaps.register()


def unregister():
    mesh_op_box.unregister()
    mesh_op_circle.unregister()
    mesh_op_lasso.unregister()
    object_op_box.unregister()
    object_op_circle.unregister()
    object_op_lasso.unregister()
    global_op.unregister()
    help.unregister()
    ui.unregister()
    tools.unregister()
    tools_dummy.unregister()
    keymaps.unregister()

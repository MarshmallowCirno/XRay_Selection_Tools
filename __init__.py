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


import importlib
from .mesh import mesh_op_box, mesh_op_circle, mesh_op_lasso
from .object import object_op_box, object_op_circle, object_op_lasso
from . import ui, tools, tools_dummy, keymaps


bl_info = {
    "name": "Select Box (X-Ray)",
    "author": "MarshmallowCirno",
    "version": (2, 0, 14),
    "blender": (2, 83, 0),
    "location": "Toolbar > Selection Tools",
    "description": "Select items using box selection. Upon selection temporary enable x-ray, "
                   "hide mirror and solidify modifiers in edit mode",
    "warning": "",
    "category": "3D View",
    "wiki_url": "https://gumroad.com/l/DaLdj",
    "tracker_url": "https://blenderartists.org/t/box-select-x-ray/1212316/1",
}


reloadable_modules = (
    "functions.mesh_modal",
    "functions.object_modal",
    "functions.intersect",
    "utils"
    "mesh.op_box",
    "mesh.op_circle",
    "mesh.op_lasso",
    "object.op_box",
    "object.op_circle",
    "object.op_lasso",
    "ui",
    "tools",
    "tools_dummy",
    "keymaps")


if "bpy" in locals():
    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])


def register():
    mesh_op_box.register()
    mesh_op_circle.register()
    mesh_op_lasso.register()
    object_op_box.register()
    object_op_circle.register()
    object_op_lasso.register()
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
    ui.unregister()
    tools.unregister()
    tools_dummy.unregister()
    keymaps.unregister()

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
    "name": "Select Box (X-Ray)",
    "author": "MarshmallowCirno",
    "version": (2, 0, 9),
    "blender": (2, 82, 0),
    "location": "Toolbar > Selection Tools",
    "description": "Select items using box selection. Upon selection temporary enable x-ray, hide mirror and solidify modifiers in edit mode",
    "warning": "Beta version",
    "category": "3D View",
    "wiki_url": "https://gumroad.com/l/DaLdj",
    "tracker_url": "https://blenderartists.org/t/box-select-x-ray/1212316/1",
}


if "bpy" in locals():
    import importlib
    reloadable_modules = [
        "functions",
        "op_box",
        "op_circle",
        "op_lasso",
        "tools",
        "ui",
        "keymaps",
        "utils"
    ]
    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])
else:
    from . import op_box, op_circle, op_lasso, tools, tools_dummy, ui, keymaps


import bpy


def register():
    op_box.register()
    op_circle.register()
    op_lasso.register()
    ui.register()
    tools.register()
    tools_dummy.register()
    keymaps.register()


def unregister():
    op_box.unregister()
    op_circle.unregister()
    op_lasso.unregister()
    ui.unregister()
    tools.unregister()
    tools_dummy.unregister()
    keymaps.unregister()

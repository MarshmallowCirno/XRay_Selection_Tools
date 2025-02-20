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
    "version": (4, 8, 0),
    "blender": (4, 3, 0),
    "location": "Toolbar > Selection Tools",
    "description": "Box, lasso and circle selection tools with x-ray",
    "warning": "",
    "category": "3D View",
    "doc_url": "https://gumroad.com/l/DaLdj",
    "tracker_url": "https://blenderartists.org/t/x-ray-selection-tools/1212316",
}

# Support reloading submodules
if "bpy" in locals():
    import sys

    from . import reloader

    reloader.reload_package_modules(sys.modules[__name__])


import bpy

# Prevent loading in the background, since gpu shaders will not be available
if not bpy.app.background:
    from . import operators, preferences, startup_handlers, tools

    def register():
        preferences.register()
        operators.register()
        tools.register()
        startup_handlers.register()

    def unregister():
        preferences.unregister()
        operators.unregister()
        tools.unregister()
        startup_handlers.unregister()
else:
    register = unregister = lambda: None

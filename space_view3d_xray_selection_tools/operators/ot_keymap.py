# pyright: reportAttributeAccessIssue = false
import bpy

from .. import addon_info

mesh_keyboard_keymap: list[tuple[bpy.types.KeyMap, bpy.types.KeyMapItem]] = []
mesh_mouse_keymap: list[tuple[bpy.types.KeyMap, bpy.types.KeyMapItem]] = []
object_keyboard_keymap: list[tuple[bpy.types.KeyMap, bpy.types.KeyMapItem]] = []
object_mouse_keymap: list[tuple[bpy.types.KeyMap, bpy.types.KeyMapItem]] = []
toggles_keymap: list[tuple[bpy.types.KeyMap, bpy.types.KeyMapItem]] = []


def _register_mesh_keyboard_keymap():
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="Mesh", space_type='EMPTY')

        kmi = km.keymap_items.new("mesh.select_lasso_xray", 'L', 'PRESS')
        kmi.properties.mode = 'ADD'
        kmi.properties.wait_for_input = True
        mesh_keyboard_keymap.append((km, kmi))

        kmi = km.keymap_items.new("mesh.select_circle_xray", 'C', 'PRESS')
        kmi.properties.mode = 'ADD'
        kmi.properties.wait_for_input = True
        mesh_keyboard_keymap.append((km, kmi))

        kmi = km.keymap_items.new("mesh.select_box_xray", 'B', 'PRESS')
        kmi.properties.mode = 'ADD'
        kmi.properties.wait_for_input = True
        mesh_keyboard_keymap.append((km, kmi))


def _register_mesh_mouse_keymap():
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="Mesh", space_type='EMPTY')

        kmi = km.keymap_items.new("mesh.select_lasso_xray", 'LEFTMOUSE', 'CLICK_DRAG', ctrl=True, shift=True)
        kmi.properties.mode = 'SUB'
        mesh_mouse_keymap.append((km, kmi))

        kmi = km.keymap_items.new("mesh.select_lasso_xray", 'LEFTMOUSE', 'CLICK_DRAG', ctrl=True)
        kmi.properties.mode = 'ADD'
        mesh_mouse_keymap.append((km, kmi))

        kmi = km.keymap_items.new("mesh.select_box_xray", 'RIGHTMOUSE', 'CLICK_DRAG', ctrl=True)
        kmi.properties.mode = 'SUB'
        mesh_mouse_keymap.append((km, kmi))

        kmi = km.keymap_items.new("mesh.select_box_xray", 'RIGHTMOUSE', 'CLICK_DRAG', shift=True)
        kmi.properties.mode = 'ADD'
        mesh_mouse_keymap.append((km, kmi))

        kmi = km.keymap_items.new("mesh.select_box_xray", 'RIGHTMOUSE', 'CLICK_DRAG')
        kmi.properties.mode = 'SET'
        mesh_mouse_keymap.append((km, kmi))


def _register_object_keyboard_keymap():
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="Object Mode", space_type='EMPTY')

        kmi = km.keymap_items.new("object.select_lasso_xray", 'L', 'PRESS')
        kmi.properties.mode = 'ADD'
        kmi.properties.wait_for_input = True
        object_keyboard_keymap.append((km, kmi))

        kmi = km.keymap_items.new("object.select_circle_xray", 'C', 'PRESS')
        kmi.properties.mode = 'ADD'
        kmi.properties.wait_for_input = True
        object_keyboard_keymap.append((km, kmi))

        kmi = km.keymap_items.new("object.select_box_xray", 'B', 'PRESS')
        kmi.properties.mode = 'ADD'
        kmi.properties.wait_for_input = True
        object_keyboard_keymap.append((km, kmi))


def _register_object_mouse_keymap():
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="Object Mode", space_type='EMPTY')

        kmi = km.keymap_items.new("object.select_lasso_xray", 'LEFTMOUSE', 'CLICK_DRAG', ctrl=True, shift=True)
        kmi.properties.mode = 'SUB'
        object_mouse_keymap.append((km, kmi))

        kmi = km.keymap_items.new("object.select_lasso_xray", 'LEFTMOUSE', 'CLICK_DRAG', ctrl=True)
        kmi.properties.mode = 'ADD'
        object_mouse_keymap.append((km, kmi))

        kmi = km.keymap_items.new("object.select_box_xray", 'RIGHTMOUSE', 'CLICK_DRAG', ctrl=True)
        kmi.properties.mode = 'SUB'
        object_mouse_keymap.append((km, kmi))

        kmi = km.keymap_items.new("object.select_box_xray", 'RIGHTMOUSE', 'CLICK_DRAG', shift=True)
        kmi.properties.mode = 'ADD'
        object_mouse_keymap.append((km, kmi))

        kmi = km.keymap_items.new("object.select_box_xray", 'RIGHTMOUSE', 'CLICK_DRAG')
        kmi.properties.mode = 'SET'
        object_mouse_keymap.append((km, kmi))


def _register_toggles_keymap():
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="Mesh", space_type='EMPTY')

        kmi = km.keymap_items.new(
            "mesh.select_tools_xray_toggle_select_backfacing", 'X', 'PRESS', ctrl=True, shift=True, alt=True
        )
        toggles_keymap.append((km, kmi))

        kmi = km.keymap_items.new("mesh.select_tools_xray_toggle_mesh_behavior", 'X', 'PRESS', ctrl=True, shift=True)
        toggles_keymap.append((km, kmi))

        kmi = km.keymap_items.new("mesh.select_tools_xray_toggle_select_through", 'X', 'PRESS', ctrl=True, alt=True)
        toggles_keymap.append((km, kmi))


def _unregister_mesh_keyboard_keymap():
    for km, kmi in mesh_keyboard_keymap:
        km.keymap_items.remove(kmi)
    mesh_keyboard_keymap.clear()


def _unregister_mesh_mouse_keymap():
    for km, kmi in mesh_mouse_keymap:
        km.keymap_items.remove(kmi)
    mesh_mouse_keymap.clear()


def _unregister_object_keyboard_keymap():
    for km, kmi in object_keyboard_keymap:
        km.keymap_items.remove(kmi)
    object_keyboard_keymap.clear()


def _unregister_object_mouse_keymap():
    for km, kmi in object_mouse_keymap:
        km.keymap_items.remove(kmi)
    object_mouse_keymap.clear()


def _unregister_toggles_keymap():
    for km, kmi in toggles_keymap:
        km.keymap_items.remove(kmi)
    toggles_keymap.clear()


def toggle_mesh_keyboard_keymap(_pg: bpy.types.PropertyGroup, _context: bpy.types.Context):
    if addon_info.get_preferences().keymaps.is_mesh_keyboard_keymap_enabled:
        _register_mesh_keyboard_keymap()
    else:
        _unregister_mesh_keyboard_keymap()


def toggle_mesh_mouse_keymap(_pg: bpy.types.PropertyGroup, _context: bpy.types.Context):
    if addon_info.get_preferences().keymaps.is_mesh_mouse_keymap_enabled:
        _register_mesh_mouse_keymap()
    else:
        _unregister_mesh_mouse_keymap()


def toggle_object_keyboard_keymap(_pg: bpy.types.PropertyGroup, _context: bpy.types.Context):
    if addon_info.get_preferences().keymaps.is_object_keyboard_keymap_enabled:
        _register_object_keyboard_keymap()
    else:
        _unregister_object_keyboard_keymap()


def toggle_object_mouse_keymap(_pg: bpy.types.PropertyGroup, _context: bpy.types.Context):
    if addon_info.get_preferences().keymaps.is_object_mouse_keymap_enabled:
        _register_object_mouse_keymap()
    else:
        _unregister_object_mouse_keymap()


def toggle_toggles_keymap(_pg: bpy.types.PropertyGroup, _context: bpy.types.Context):
    if addon_info.get_preferences().keymaps.is_toggles_keymap_enabled:
        _register_toggles_keymap()
    else:
        _unregister_toggles_keymap()


def register():
    if addon_info.get_preferences().keymaps.is_mesh_mouse_keymap_enabled:
        _register_mesh_mouse_keymap()
    if addon_info.get_preferences().keymaps.is_mesh_keyboard_keymap_enabled:
        _register_mesh_keyboard_keymap()
    if addon_info.get_preferences().keymaps.is_object_mouse_keymap_enabled:
        _register_object_mouse_keymap()
    if addon_info.get_preferences().keymaps.is_object_keyboard_keymap_enabled:
        _register_object_keyboard_keymap()
    if addon_info.get_preferences().keymaps.is_toggles_keymap_enabled:
        _register_toggles_keymap()


def unregister():
    _unregister_mesh_mouse_keymap()
    _unregister_mesh_keyboard_keymap()
    _unregister_object_mouse_keymap()
    _unregister_object_keyboard_keymap()
    _unregister_toggles_keymap()

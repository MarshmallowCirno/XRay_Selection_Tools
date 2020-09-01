import bpy


addon_keymaps = []


def register_keymaps():    
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        # mesh mode
        km = kc.keymaps.new(name="Mesh", space_type='EMPTY')

        kmi = km.keymap_items.new("mesh.select_tools_xray_toggle_select_through", 'X', 'PRESS', ctrl=True, alt=True)
        kmi.active = False
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new("mesh.select_lasso_xray", 'EVT_TWEAK_L', 'ANY', ctrl=True, shift=True)
        kmi.properties.mode = 'SUB'
        kmi.active = False
        addon_keymaps.append((km, kmi))
        
        kmi = km.keymap_items.new("mesh.select_lasso_xray", 'EVT_TWEAK_L', 'ANY', ctrl=True)
        kmi.properties.mode = 'ADD'
        kmi.active = False
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new("mesh.select_box_xray", 'EVT_TWEAK_R', 'ANY', ctrl=True)
        kmi.properties.mode = 'SUB'
        kmi.active = False
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new("mesh.select_box_xray", 'EVT_TWEAK_R', 'ANY', shift=True)
        kmi.properties.mode = 'ADD'
        kmi.active = False
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new("mesh.select_box_xray", 'EVT_TWEAK_R', 'ANY')
        kmi.properties.mode = 'SET'
        kmi.active = False
        addon_keymaps.append((km, kmi))
        
        kmi = km.keymap_items.new("mesh.select_lasso_xray", 'L', 'PRESS')
        kmi.properties.mode = 'ADD'
        kmi.properties.wait_for_input = True
        kmi.active = True
        addon_keymaps.append((km, kmi))
        
        kmi = km.keymap_items.new("mesh.select_circle_xray", 'C', 'PRESS')
        kmi.properties.mode = 'ADD'
        kmi.properties.wait_for_input = True
        kmi.active = True
        addon_keymaps.append((km, kmi))
        
        kmi = km.keymap_items.new("mesh.select_box_xray", 'B', 'PRESS')
        kmi.properties.mode = 'ADD'
        kmi.properties.wait_for_input = True
        kmi.active = True
        addon_keymaps.append((km, kmi))

        # object mode
        km = kc.keymaps.new(name="Object Mode", space_type='EMPTY')

        kmi = km.keymap_items.new("object.select_lasso_xray", 'EVT_TWEAK_L', 'ANY', ctrl=True, shift=True)
        kmi.properties.mode = 'SUB'
        kmi.active = False
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new("object.select_lasso_xray", 'EVT_TWEAK_L', 'ANY', ctrl=True)
        kmi.properties.mode = 'ADD'
        kmi.active = False
        addon_keymaps.append((km, kmi))
        
        kmi = km.keymap_items.new("object.select_box_xray", 'EVT_TWEAK_R', 'ANY', ctrl=True)
        kmi.properties.mode = 'SUB'
        kmi.active = False
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new("object.select_box_xray", 'EVT_TWEAK_R', 'ANY', shift=True)
        kmi.properties.mode = 'ADD'
        kmi.active = False
        addon_keymaps.append((km, kmi))
        
        kmi = km.keymap_items.new("object.select_box_xray", 'EVT_TWEAK_R', 'ANY')
        kmi.properties.mode = 'SET'
        kmi.active = False
        addon_keymaps.append((km, kmi))
        
        kmi = km.keymap_items.new("object.select_lasso_xray", 'L', 'PRESS')
        kmi.properties.mode = 'ADD'
        kmi.properties.wait_for_input = True
        kmi.active = True
        addon_keymaps.append((km, kmi))
        
        kmi = km.keymap_items.new("object.select_circle_xray", 'C', 'PRESS')
        kmi.properties.mode = 'ADD'
        kmi.properties.wait_for_input = True
        kmi.active = True
        addon_keymaps.append((km, kmi))
        
        kmi = km.keymap_items.new("object.select_box_xray", 'B', 'PRESS')
        kmi.properties.mode = 'ADD'
        kmi.properties.wait_for_input = True
        kmi.active = True
        addon_keymaps.append((km, kmi))


def unregister_keymaps():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
    
def register():
    register_keymaps()


def unregister():
    unregister_keymaps()

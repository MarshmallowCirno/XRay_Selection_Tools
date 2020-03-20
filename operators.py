import bpy
from .functions import select_elems_in_rectangle
from .keymaps import addon_keymaps


class OBJECT_OT_select_box_xray(bpy.types.Operator):
    '''Select items using box selection with x-ray'''
    bl_idname = "object.select_box_xray"
    bl_label = "Box Select X-Ray"
    bl_options = {'REGISTER'}
    
    mode: bpy.props.EnumProperty(                        
        name = "Mode", 
        items = [('SET', "Set", "Set a new selection", 'SELECT_SET', 1),
             ('ADD', "Extend", "Extend existing selection", 'SELECT_EXTEND', 2),
             ('SUB', "Substract", "Substract existing selection", 'SELECT_SUBTRACT', 3),
             ('XOR', "Difference", "Inverts existing selection", 'SELECT_DIFFERENCE', 4),
             ('AND', "Intersect", "Intersect existing selection", 'SELECT_INTERSECT', 5)
        ],
        default = 'SET'
    )
    wait_for_input: bpy.props.BoolProperty(                        
        name = "Wait for input",
        description = "Wait for mouse input or initialize box selection immediately (enable when assigning the operator to a keyboard key)", 
        default = False
    )

    @classmethod
    def poll(cls, context):
        return (context.area.type == 'VIEW_3D' and context.mode == 'OBJECT')

    def invoke(self, context, event):
        self.init_show_xray = context.space_data.shading.show_xray
      
        context.window_manager.modal_handler_add(self)
        self.select_box_xray(context)
        return {'RUNNING_MODAL'}
        
    def select_box_xray(self, context):
        if not self.init_show_xray:
           context.space_data.shading.show_xray = True    

        bpy.ops.view3d.select_box('INVOKE_DEFAULT', mode=self.mode, wait_for_input=self.wait_for_input)

    def modal(self, context, event):
        if event.value == 'RELEASE' or event.type in ('ESC', 'RIGHTMOUSE'):
            self.finish(context)
            return {'FINISHED'}
        
        return {'RUNNING_MODAL'}

    def finish(self, context):
        if not self.init_show_xray:
            context.space_data.shading.show_xray = False

        
class MESH_OT_select_box_xray(bpy.types.Operator):
    '''Select items using box selection with x-ray'''
    bl_idname = "mesh.select_box_xray"
    bl_label = "Box Select X-Ray"
    bl_options = {'REGISTER', 'GRAB_CURSOR'}
    
    mode: bpy.props.EnumProperty(                        
        name = "Mode", 
        items = [('SET', "Set", "Set a new selection", 'SELECT_SET', 1),
             ('ADD', "Extend", "Extend existing selection", 'SELECT_EXTEND', 2),
             ('SUB', "Substract", "Substract existing selection", 'SELECT_SUBTRACT', 3),
             ('XOR', "Difference", "Inverts existing selection", 'SELECT_DIFFERENCE', 4),
             ('AND', "Intersect", "Intersect existing selection", 'SELECT_INTERSECT', 5)
        ],
        default = 'SET'
    )
    wait_for_input: bpy.props.BoolProperty(                        
        name = "Wait for input",
        description = "Wait for mouse input or initialize box selection immediately (enable when assigning the operator to a keyboard key)", 
        default = False
    )
    select_all_faces: bpy.props.BoolProperty(                        
        name = "Select All Faces",
        description = "Additionally select faces that are partially inside the selection box, not just the ones with centers inside the selection box. Works only in select through mode", 
        default = False
    )
    select_all_edges: bpy.props.BoolProperty(                        
        name = "Select All Edges",
        description = "Additionally select edges that are partially inside the selection box, not just the ones completely inside the selection box. Works only in select through mode", 
        default = False
    )
    show_xray: bpy.props.BoolProperty(                        
        name = "Show X-Ray",
        description = "Enable x-ray shading during selection",
        default = True
    )
    select_through: bpy.props.BoolProperty(                        
        name = "Select Through",
        description = "Select verts, faces and edges laying underneath",
        default = True
    )
    hide_modifiers: bpy.props.BoolProperty(                        
        name = "Hide Modifiers",
        description = "Hide mirror and solidify modifiers during selection",
        default = True
    )
    
    @classmethod
    def poll(cls, context):
        return (context.area.type == 'VIEW_3D' and context.mode == 'EDIT_MESH')
        
    def __init__(self):
        self.init_mod_states = []
        self.custom_selection = False
        
    def invoke(self, context, event):
        # if select through is disabled, use default "box select" without any optional features
        if self.select_through:
            # save initial modifier states to restore them later
            if self.hide_modifiers:
                mods_to_hide = ('MIRROR', 'SOLIDIFY') if self.show_xray else ('MIRROR')
                for ob in context.selected_objects:
                    self.init_mod_states.extend([(m, m.show_in_editmode) for m in ob.modifiers if m.type in mods_to_hide])
                    
            # save initial x-ray properties to restore them later
            self.init_show_xray = context.space_data.shading.show_xray
            self.init_xray_alpha = context.space_data.shading.xray_alpha
            self.init_show_faces = context.space_data.overlay.show_faces
            
            # elements that can't be selected with default box select should be selected with custom selection
            self.custom_selection = (self.select_all_faces and context.tool_settings.mesh_select_mode[2]) or (self.select_all_edges and context.tool_settings.mesh_select_mode[1])
            if self.custom_selection:
                # save initial mouse location to calculate box coordinates for custom selection
                self.init_mouse_x = event.mouse_region_x
                self.init_mouse_y = event.mouse_region_y
                # disable confirmation in default box selection 
                self.disable_box_selection()
                
            # disable modifiers and set x-ray state
            self.set_visual_display(context)
            
        context.window_manager.modal_handler_add(self)
        # start default box select modal
        bpy.ops.view3d.select_box('INVOKE_DEFAULT', mode=self.mode, wait_for_input=self.wait_for_input)
        return {'RUNNING_MODAL'}
               
    def disable_box_selection(self):
        '''Disable default "box select" tool confirmation by adding "cancel" key to its modal keymaps, 
        since actual selection will be made with the addon and default "box select" only needed for drawing fast rectangle shader'''
        kc = bpy.context.window_manager.keyconfigs.addon
        km = kc.keymaps.new(name="Gesture Box", space_type='EMPTY', region_type='WINDOW', modal=True)
        kmi = km.keymap_items.new_modal('CANCEL', 'LEFTMOUSE', 'RELEASE', any=True)
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new_modal('CANCEL', 'RIGHTMOUSE', 'RELEASE', any=True)
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new_modal('CANCEL', 'MIDDLEMOUSE', 'RELEASE', any=True)
        addon_keymaps.append((km, kmi))

    def set_visual_display(self, context):
        '''Disable modifiers and set x-ray state'''
        # if xray already enabled, nothing should be changed here
        if not self.init_show_xray:
            # if user wants to use xray, enable it
            if self.show_xray:
                context.space_data.shading.show_xray = True
            # otherwise use it, but hide shading
            # custom selection don't need it
            elif not self.custom_selection:
                context.space_data.shading.show_xray = True
                context.space_data.shading.xray_alpha = 1
                context.space_data.overlay.show_faces = False
        # hide modifiers
        if self.init_mod_states:
            for mod, state in self.init_mod_states:
                mod.show_in_editmode = False

    def modal(self, context, event):
    
        if event.value == 'RELEASE' or event.type in ('ESC', 'RIGHTMOUSE'):
            self.finish(context, event)
            return {'FINISHED'}
        
        return {'RUNNING_MODAL'}
        
    def restore_box_selection(self):
        '''Restore default "box select" keymap'''
        for km, kmi in reversed(addon_keymaps):
            if km.name == "Gesture Box":
                addon_keymaps.remove((km, kmi))
                km.keymap_items.remove(kmi)

    def finish(self, context, event):
        # if select through was disabled, nothing was changed and nothing to restore
        if self.select_through:
            # if xray was already enabled, nothing to restore
            if not self.init_show_xray:
                # if xray shading was enabled by user preferences, disable it
                if self.show_xray:
                    context.space_data.shading.show_xray = False
                # otherwise if xray was still used without alpha, disable it and restore alpha
                elif not self.custom_selection:
                    context.space_data.shading.show_xray = False
                    context.space_data.shading.xray_alpha = self.init_xray_alpha
                    context.space_data.overlay.show_faces = self.init_show_faces

            # default "box select" wasn't used, select manually
            if self.custom_selection:
                # restore default box select confirmation
                self.restore_box_selection()
                # get selection rectangle coordinates
                xmin = min(self.init_mouse_x, event.mouse_region_x)
                xmax = max(self.init_mouse_x, event.mouse_region_x)
                ymin = min(self.init_mouse_y, event.mouse_region_y)
                ymax = max(self.init_mouse_y, event.mouse_region_y)
                # do selection
                select_elems_in_rectangle(context, mode=self.mode, select_all_edges=self.select_all_edges, \
                select_all_faces=self.select_all_faces, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
                
                bpy.ops.ed.undo_push(message="Box Select")
                
            # restore modifier states
            if self.init_mod_states:
                for mod, state in self.init_mod_states:
                    mod.show_in_editmode = state
                    
                    
classes = (
    OBJECT_OT_select_box_xray,
    MESH_OT_select_box_xray
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)

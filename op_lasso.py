import bpy
from .functions import select_elems_in_rectangle


class OBJECT_OT_select_lasso_xray(bpy.types.Operator):
    '''Select items using lasso selection with x-ray'''
    bl_idname = "object.select_lasso_xray"
    bl_label = "Lasso Select X-Ray"
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
        description = "Wait for mouse input or initialize lasso selection immediately (enable when assigning the operator to a keyboard key)", 
        default = False
    )
    show_xray: bpy.props.BoolProperty(                        
        name = "Show X-Ray",
        description = "Enable x-ray shading during selection",
        default = True
    )

    @classmethod
    def poll(cls, context):
        return (context.area.type == 'VIEW_3D' and context.mode == 'OBJECT')

    def __init__(self):
        self.started = not self.wait_for_input

    def invoke(self, context, event):
        self.init_show_xray = context.space_data.shading.show_xray
        self.init_show_xray_wireframe = context.space_data.shading.show_xray_wireframe
      
        self.set_visual_display(context)
      
        context.window_manager.modal_handler_add(self)
        
        if self.started:
            bpy.ops.view3d.select_lasso('INVOKE_DEFAULT', mode=self.mode)
        else:
            context.window.cursor_modal_set('CROSSHAIR')
            context.workspace.status_text_set(text="RMB, ESC: Cancel  |  LMB: Begin") 
        return {'RUNNING_MODAL'}
        
    def set_visual_display(self, context):
        if self.show_xray and ((context.space_data.shading.type in {'SOLID','MATERIAL','RENDERED'} and not self.init_show_xray)\
        or (context.space_data.shading.type == 'WIREFRAME' and not self.init_show_xray_wireframe)):
           context.space_data.shading.show_xray = True
           context.space_data.shading.show_xray_wireframe = True
           
    def modal(self, context, event): 
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            self.finish(context)
            return {'FINISHED'}
    
        if self.started:
            if event.value == 'RELEASE':
                self.finish(context)
                return {'FINISHED'}
        else:
            if event.value == 'PRESS' and event.type in {'LEFTMOUSE','MIDDLEMOUSE'}:
                self.started = True
                if event.shift:
                    self.mode = 'SUB'
                bpy.ops.view3d.select_lasso('INVOKE_DEFAULT', mode=self.mode)
        
        return {'RUNNING_MODAL'}

    def finish(self, context):
        context.space_data.shading.show_xray = self.init_show_xray
        context.space_data.shading.show_xray_wireframe = self.init_show_xray_wireframe
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(text=None)
        
        
class MESH_OT_select_lasso_xray(bpy.types.Operator):
    '''Select items using lasso selection with x-ray'''
    bl_idname = "mesh.select_lasso_xray"
    bl_label = "Lasso Select X-Ray"
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
        description = "Wait for mouse input or initialize lasso selection immediately (enable when assigning the operator to a keyboard key)", 
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
        self.started = not self.wait_for_input
        
    def invoke(self, context, event):
        # if select through is disabled, use default "lasso select" without any optional features
        if self.select_through:
            # save initial modifier states to restore them later
            if self.hide_modifiers:
                mods_to_hide = ('MIRROR', 'SOLIDIFY') if self.show_xray else ('MIRROR')
                sel_obs = context.selected_objects if context.selected_objects else [context.object]
                for ob in sel_obs:
                    self.init_mod_states.extend([(m, m.show_in_editmode) for m in ob.modifiers if m.type in mods_to_hide])
                    
            # save initial x-ray properties to restore them later
            self.init_show_xray = context.space_data.shading.show_xray
            self.init_xray_alpha = context.space_data.shading.xray_alpha
            self.init_show_xray_wireframe = context.space_data.shading.show_xray_wireframe
            self.init_xray_alpha_wireframe = context.space_data.shading.xray_alpha_wireframe
            self.init_backwire_opacity = context.space_data.overlay.backwire_opacity

            # disable modifiers and set x-ray state
            self.set_visual_display(context)
            
        context.window_manager.modal_handler_add(self)
        
        # start default lasso select modal
        if self.started:
            bpy.ops.view3d.select_lasso('INVOKE_DEFAULT', mode=self.mode)
        else:
            context.window.cursor_modal_set('CROSSHAIR')
            context.workspace.status_text_set(text="RMB, ESC: Cancel  |  LMB: Begin") 
        return {'RUNNING_MODAL'}

    def set_visual_display(self, context):
        '''Disable modifiers and set x-ray state'''
        # if xray already enabled, nothing should be changed here
        if (context.space_data.shading.type in {'SOLID','MATERIAL','RENDERED'} and not self.init_show_xray) or (context.space_data.shading.type == 'WIREFRAME' and not self.init_show_xray_wireframe):
            # if user wants to use xray, enable it
            if self.show_xray:
                context.space_data.shading.show_xray = True
                context.space_data.shading.show_xray_wireframe = True
            # otherwise enable it, but hide shading
            else:
                context.space_data.shading.show_xray = True
                context.space_data.shading.show_xray_wireframe = True
                context.space_data.shading.xray_alpha = 1
                context.space_data.shading.xray_alpha_wireframe = 1
                context.space_data.overlay.backwire_opacity = 0
                
        # hide modifiers
        if self.init_mod_states:
            for mod, state in self.init_mod_states:
                mod.show_in_editmode = False

    def modal(self, context, event):
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            self.finish(context)
            return {'FINISHED'}
    
        if self.started:
            if event.value == 'RELEASE':
                self.finish(context)
                return {'FINISHED'}
        else:
            if event.value == 'PRESS' and event.type in {'LEFTMOUSE','MIDDLEMOUSE'}:
                self.started = True
                if event.shift:
                    self.mode = 'SUB'
                bpy.ops.view3d.select_lasso('INVOKE_DEFAULT', mode=self.mode)
                
        return {'RUNNING_MODAL'}
        
    def finish(self, context):
        # if select through was disabled, nothing was changed and nothing to restore
        if self.select_through:
            context.space_data.shading.show_xray = self.init_show_xray
            context.space_data.shading.xray_alpha = self.init_xray_alpha
            context.space_data.shading.show_xray_wireframe = self.init_show_xray_wireframe
            context.space_data.shading.xray_alpha_wireframe = self.init_xray_alpha_wireframe
            context.space_data.overlay.backwire_opacity = self.init_backwire_opacity

            # restore modifier states
            if self.init_mod_states:
                for mod, state in self.init_mod_states:
                    mod.show_in_editmode = state
                    
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(text=None)


classes = (
    OBJECT_OT_select_lasso_xray,
    MESH_OT_select_lasso_xray
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)

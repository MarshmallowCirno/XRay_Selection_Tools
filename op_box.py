import bpy, gpu, bgl
from .functions import select_elems_in_rectangle
from struct import pack
from gpu_extras.batch import batch_for_shader
from bgl import glEnable, glDisable, GL_BLEND


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
    show_xray: bpy.props.BoolProperty(                        
        name = "Show X-Ray",
        description = "Enable x-ray shading during selection",
        default = True
    )

    @classmethod
    def poll(cls, context):
        return (context.area.type == 'VIEW_3D' and context.mode == 'OBJECT')

    def invoke(self, context, event):
        self.init_show_xray = context.space_data.shading.show_xray
        self.init_show_xray_wireframe = context.space_data.shading.show_xray_wireframe
      
        context.window_manager.modal_handler_add(self)
        self.select_box_xray(context)
        return {'RUNNING_MODAL'}
        
    def select_box_xray(self, context):
        if self.show_xray and ((context.space_data.shading.type in {'SOLID','MATERIAL','RENDERED'} and not self.init_show_xray)\
        or (context.space_data.shading.type == 'WIREFRAME' and not self.init_show_xray_wireframe)):
           context.space_data.shading.show_xray = True
           context.space_data.shading.show_xray_wireframe = True

        bpy.ops.view3d.select_box('INVOKE_DEFAULT', mode=self.mode, wait_for_input=self.wait_for_input)

    def modal(self, context, event):
        if event.value == 'RELEASE' or event.type in ('ESC', 'RIGHTMOUSE'):
            self.finish(context)
            return {'FINISHED'}
        
        return {'RUNNING_MODAL'}

    def finish(self, context):
        context.space_data.shading.show_xray = self.init_show_xray
        context.space_data.shading.show_xray_wireframe = self.init_show_xray_wireframe

        
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
        description = "Enable x-ray shading during selection. Works only in select through mode",
        default = True
    )
    select_through: bpy.props.BoolProperty(                        
        name = "Select Through",
        description = "Select verts, faces and edges laying underneath",
        default = True
    )
    hide_modifiers: bpy.props.BoolProperty(                        
        name = "Hide Modifiers",
        description = "Hide mirror and solidify modifiers during selection. Works only in select through mode",
        default = True
    )
    
    @classmethod
    def poll(cls, context):
        return (context.area.type == 'VIEW_3D' and context.mode == 'EDIT_MESH')
        
    def __init__(self):
        self.custom_selection = False
        self.custom_preselection = self.wait_for_input
        self.preselection_xray = False
    
        self.init_mod_states = []
        self.init_gesture_box_keymaps = []
        self.new_gesture_box_keymaps = []
        
        self.vertex_shader = '''
            in vec2 pos;
            in float len;
            
            uniform mat4 u_ViewProjectionMatrix;
            uniform float u_X;
            uniform float u_Y;
            
            out float v_Len;

            void main()
            {
                v_Len = len;
                gl_Position = u_ViewProjectionMatrix * vec4(pos.x + u_X, pos.y + u_Y, 0.0f, 1.0f);
            }
        '''
        # https://docs.blender.org/api/blender2.8/gpu.html#custom-shader-for-dotted-3d-line
        # https://stackoverflow.com/questions/52928678/dashed-line-in-opengl3
        self.fragment_shader = '''
            in float v_Len;
            
            uniform vec4 u_ColorMain;
            uniform vec4 u_ColorGap;
            
            float dash_size = 4;
            float gap_size = 4;
            vec4 col = u_ColorMain;

            void main()
            {
                if (fract(v_Len/(dash_size + gap_size)) > dash_size/(dash_size + gap_size)) 
                    col = u_ColorGap;
                    
                gl_FragColor = col;
            }
        '''
        
    def invoke(self, context, event):
        # if select through and visual display would be changed or may be changed
        if self.select_through or self.custom_preselection:
            # save initial modifier states to restore them later
            if self.hide_modifiers:
                mods_to_hide = {'MIRROR', 'SOLIDIFY'} if self.show_xray else {'MIRROR'}
                sel_obs = context.selected_objects if context.selected_objects else [context.object]
                for ob in sel_obs:
                    self.init_mod_states.extend([(m, m.show_in_editmode) for m in ob.modifiers if m.type in mods_to_hide])
                
            # save initial x-ray properties to restore them later
            self.init_show_xray = context.space_data.shading.show_xray
            self.init_xray_alpha = context.space_data.shading.xray_alpha
            self.init_show_xray_wireframe = context.space_data.shading.show_xray_wireframe
            self.init_xray_alpha_wireframe = context.space_data.shading.xray_alpha_wireframe
            self.init_backwire_opacity = context.space_data.overlay.backwire_opacity
        
            # decide whether elements that can't be selected with the default box select operator should be selected with custom intersection tests
            self.custom_selection = self.select_all_faces and context.tool_settings.mesh_select_mode[2] or self.select_all_edges and context.tool_settings.mesh_select_mode[1]
           
        # disable modifiers and set x-ray states
        if self.select_through:
            self.update_visual_display(context)
            
        context.window_manager.modal_handler_add(self)
               
        if self.custom_preselection:
            # draw status, header and shader
            context.window.cursor_modal_set('CROSSHAIR')
            context.workspace.status_text_set(text="RMB, ESC: Cancel  |  LMB: Begin")
            
            width = context.region.width
            height = context.region.height

            vertices = ((0, -height),
                        (0, height),
                        (-width, 0),
                        (width, 0))
            lengths = (0, 2*height, 0, 2*width)
            
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y
            
            self.shader = gpu.types.GPUShader(self.vertex_shader, self.fragment_shader)
            self.batch = batch_for_shader(self.shader, 'LINES', {"pos":vertices, "len":lengths})
            self.unif_color_main = self.shader.uniform_from_name("u_ColorMain")
            self.unif_color_gap = self.shader.uniform_from_name("u_ColorGap")
            
            self.handler = context.space_data.draw_handler_add(self.draw_shader,(context,),'WINDOW','POST_PIXEL')
            context.region.tag_redraw()
            
            if context.space_data.shading.type in {'SOLID','MATERIAL','RENDERED'} and self.init_show_xray\
            or context.space_data.shading.type == 'WIREFRAME' and self.init_show_xray_wireframe:
                self.show_xray = True
                self.select_through = True
        else:
            self.begin_box_selection(context, event)
            
        return {'RUNNING_MODAL'}
                
    def modal(self, context, event):
        # cancel modal
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            if self.select_through and self.custom_selection:
                self.restore_box_selection()
                    
            if self.select_through or self.wait_for_input:
                self.restore_visual_display(context)
            
            if self.custom_preselection:
                self.finish_custom_preselection(context)
            return {'CANCELLED'}
            
        if self.custom_preselection:
            # update crossed lines shader
            if event.type == 'MOUSEMOVE':
                self.mouse_x = event.mouse_region_x
                self.mouse_y = event.mouse_region_y
                context.region.tag_redraw()
        
            # finish custom preselection mode
            if event.value == 'PRESS' and event.type in {'LEFTMOUSE', 'MIDDLEMOUSE'}:
                # restore status and header text, remove shader
                self.finish_custom_preselection(context)
                if event.shift:
                    self.mode = 'SUB'
                self.begin_box_selection(context, event)
                
            # toggle select through
            if event.value in {'PRESS', 'RELEASE'} and event.type in {'LEFT_ALT', 'RIGHT_ALT'}:
                self.select_through = not self.select_through
                self.update_visual_display(context)
                context.region.tag_redraw()
        else:
            # finish selection
            if event.value == 'RELEASE':
                self.finish(context, event)
                return {'FINISHED'}

        return {'RUNNING_MODAL'}
        
    def begin_box_selection(self, context, event):
        if self.select_through and self.custom_selection:
            # save initial mouse location to calculate box coordinates for custom selection
            self.init_mouse_x = event.mouse_region_x
            self.init_mouse_y = event.mouse_region_y
            # disable default box selection operator
            self.disable_box_selection()
        
        bpy.ops.view3d.select_box('INVOKE_DEFAULT', mode=self.mode, wait_for_input=False)
        
    def update_visual_display(self, context):
        if self.show_xray:
            context.space_data.shading.show_xray = self.select_through
            context.space_data.shading.show_xray_wireframe = self.select_through
        else:
            if not self.custom_selection:
                context.space_data.shading.show_xray = self.select_through
                context.space_data.shading.show_xray_wireframe = self.select_through
                context.space_data.shading.xray_alpha = 1 if self.select_through else self.init_show_xray_wireframe
                context.space_data.shading.xray_alpha_wireframe = 1 if self.select_through else self.init_xray_alpha_wireframe
                context.space_data.overlay.backwire_opacity = 0 if self.select_through else self.init_backwire_opacity
        
        if self.init_mod_states:
            for mod, state in self.init_mod_states:
                if self.select_through:
                    if mod.show_in_editmode:
                        mod.show_in_editmode = False
                else:
                    if mod.show_in_editmode != state:
                        mod.show_in_editmode = state

    def restore_visual_display(self, context):
        context.space_data.shading.show_xray = self.init_show_xray
        context.space_data.shading.xray_alpha = self.init_xray_alpha
        context.space_data.shading.show_xray_wireframe = self.init_show_xray_wireframe
        context.space_data.shading.xray_alpha_wireframe = self.init_xray_alpha_wireframe
        context.space_data.overlay.backwire_opacity = self.init_backwire_opacity
        
        if self.init_mod_states:
            for mod, state in self.init_mod_states:
                if mod.show_in_editmode != state:
                    mod.show_in_editmode = state
        
    def disable_box_selection(self):
        '''Temporary disable the default "box select" tool confirmation by adding the "cancel" keys to its modal keymaps
        and deactivating default confirmation keymaps, since actual selection will be made with the addon 
        and the default "box select" only needed for drawing the fast rectangle shader'''
        kc = bpy.context.window_manager.keyconfigs.user
        # save default keymap states and deactivate them
        km = kc.keymaps["Gesture Box"]
        for kmi in km.keymap_items:
            if kmi.propvalue != 'BEGIN':
                self.init_gesture_box_keymaps.append((kmi.id, kmi.active))
                kmi.active = False
        
        # add the new cancel keymaps
        km = kc.keymaps.new(name="Gesture Box", space_type='EMPTY', region_type='WINDOW', modal=True)
        kmi = km.keymap_items.new_modal('CANCEL', 'LEFTMOUSE', 'RELEASE', any=True)
        self.new_gesture_box_keymaps.append(kmi.id)
        kmi = km.keymap_items.new_modal('CANCEL', 'RIGHTMOUSE', 'RELEASE', any=True)
        self.new_gesture_box_keymaps.append(kmi.id)
        kmi = km.keymap_items.new_modal('CANCEL', 'MIDDLEMOUSE', 'RELEASE', any=True)
        self.new_gesture_box_keymaps.append(kmi.id)

    def restore_box_selection(self):
        '''Restore initial "box select" keymaps'''
        kc = bpy.context.window_manager.keyconfigs.user
        km = kc.keymaps["Gesture Box"]
        
        for id, active in self.init_gesture_box_keymaps:
            kmi = km.keymap_items.from_id(id)
            kmi.active = active
            
        for id in self.new_gesture_box_keymaps:
            kmi = km.keymap_items.from_id(id)
            km.keymap_items.remove(kmi)

    def finish(self, context, event):
        if self.select_through: 
             # default "box select" wasn't used, select with custom intersection tests
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
                
        if self.select_through or self.wait_for_input:
            self.restore_visual_display(context)
        
    def finish_custom_preselection(self, context):
        self.custom_preselection = False
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(text=None)
        context.space_data.draw_handler_remove(self.handler, 'WINDOW')
        context.region.tag_redraw()

    def draw_shader(self, context):
        self.shader.bind()
        matrix = gpu.matrix.get_projection_matrix()
        color_main = (1.0, 1.0, 1.0, 1.0)
        color_gap = (0.5, 0.5, 0.5, 1.0)
        self.shader.uniform_float("u_ViewProjectionMatrix", matrix)
        self.shader.uniform_vector_float(self.unif_color_main, pack("4f", *color_main), 4)
        self.shader.uniform_vector_float(self.unif_color_gap, pack("4f", *color_gap), 4)
        self.shader.uniform_float("u_X", self.mouse_x)
        self.shader.uniform_float("u_Y", self.mouse_y)
        self.batch.draw(self.shader)


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

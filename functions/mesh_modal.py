from .. preferences import get_preferences


def gather_overlays(context):
    overlays = {"show_xray": context.space_data.shading.show_xray,
                "xray_alpha": context.space_data.shading.xray_alpha,
                "show_xray_wireframe": context.space_data.shading.show_xray_wireframe,
                "xray_alpha_wireframe": context.space_data.shading.xray_alpha_wireframe,
                "backwire_opacity": context.space_data.overlay.backwire_opacity}
    return overlays


def gather_modifiers(context):
    mods = []
    mods_to_hide = {'MIRROR', 'SOLIDIFY'}
    sel_obs = context.selected_objects if context.selected_objects else [context.object]
    for ob in sel_obs:
        mods.extend([(m, m.show_in_editmode) for m in ob.modifiers if m.type in mods_to_hide])
    return mods


def toggle_overlays(self, context):
    """Hide or show xray to enable or disable selection through if custom intersection
    tests aren't used. If displaying of xray disabled in operator parameters, mask it
    with shading settings"""
    if self.show_xray:
        context.space_data.shading.show_xray = self.select_through
        context.space_data.shading.show_xray_wireframe = self.select_through
    else:
        if not self.override_intersect_tests:
            context.space_data.shading.show_xray = self.select_through
            context.space_data.shading.show_xray_wireframe = self.select_through
            if self.select_through:
                context.space_data.shading.xray_alpha = 1
                context.space_data.shading.xray_alpha_wireframe = 1
                context.space_data.overlay.backwire_opacity = 0
            else:
                context.space_data.shading.xray_alpha = self.init_overlays["show_xray_wireframe"]
                context.space_data.shading.xray_alpha_wireframe = self.init_overlays["xray_alpha_wireframe"]
                context.space_data.overlay.backwire_opacity = self.init_overlays["backwire_opacity"]


def toggle_modifiers(self):
    """Hide modifiers in editmode or restore initial visibility"""
    if self.init_mods:
        if self.select_through:
            for mod, show_in_editmode in self.init_mods:
                if mod.show_in_editmode:
                    mod.show_in_editmode = False
        else:
            for mod, show_in_editmode in self.init_mods:
                if mod.show_in_editmode != show_in_editmode:
                    mod.show_in_editmode = show_in_editmode


def restore_overlays(self, context):
    if self.init_overlays:
        context.space_data.shading.show_xray = self.init_overlays["show_xray"]
        context.space_data.shading.xray_alpha = self.init_overlays["xray_alpha"]
        context.space_data.shading.show_xray_wireframe = self.init_overlays["show_xray_wireframe"]
        context.space_data.shading.xray_alpha_wireframe = self.init_overlays["xray_alpha_wireframe"]
        context.space_data.overlay.backwire_opacity = self.init_overlays["backwire_opacity"]
    

def restore_modifiers(self):
    if self.init_mods:
        for mod, show_in_editmode in self.init_mods:
            if mod.show_in_editmode != show_in_editmode:
                mod.show_in_editmode = show_in_editmode


def get_select_through_toggle_keys():
    return {
        'CTRL': {'LEFT_CTRL', 'RIGHT_CTRL'},
        'ALT': {'LEFT_ALT', 'RIGHT_ALT'},
        'SHIFT': {'LEFT_SHIFT', 'RIGHT_SHIFT'},
        'DISABLED': {'DISABLED'}
    }[get_preferences().select_through_toggle_key]


def get_alter_mode_toggle_keys():
    return {
        'CTRL': {'LEFT_CTRL', 'RIGHT_CTRL'},
        'ALT': {'LEFT_ALT', 'RIGHT_ALT'},
        'SHIFT': {'LEFT_SHIFT', 'RIGHT_SHIFT'}
    }[get_preferences().alter_mode_toggle_key]


def toggle_alter_mode(self, event):
    if event.ctrl and self.alter_mode_toggle_key == 'CTRL' or \
            event.alt and self.alter_mode_toggle_key == 'ALT' or \
            event.shift and self.alter_mode_toggle_key == 'SHIFT':
        self.mode = self.alter_mode


def sync_select_through(self, context):
    """Sync operator parameters to context shading. So if xray already enabled
    make sure it would be possible to toggle it regardless of operator parameters"""
    # second time during select_through toggling
    if context.space_data.shading.type in {'SOLID', 'MATERIAL', 'RENDERED'} and \
            context.space_data.shading.show_xray or \
            context.space_data.shading.type == 'WIREFRAME' and \
            context.space_data.shading.show_xray_wireframe:
        self.show_xray = True
        self.select_through = True

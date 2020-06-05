from .. preferences import get_preferences


def gather_overlays(context):
    overlays = {"show_xray": context.space_data.shading.show_xray,
                "show_xray_wireframe": context.space_data.shading.show_xray_wireframe}
    return overlays


def toggle_overlays(self, context):
    if self.show_xray:
        if context.space_data.shading.type in {'SOLID', 'MATERIAL', 'RENDERED'} and \
                not self.init_overlays["show_xray"]:
            context.space_data.shading.show_xray = True
        elif context.space_data.shading.type == 'WIREFRAME' and \
                not self.init_overlays["show_xray_wireframe"]:
            context.space_data.shading.show_xray_wireframe = True


def restore_overlays(self, context):
    if self.init_overlays:
        context.space_data.shading.show_xray = self.init_overlays["show_xray"]
        context.space_data.shading.show_xray_wireframe = self.init_overlays["show_xray_wireframe"]


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

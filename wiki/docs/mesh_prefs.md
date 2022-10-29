#

![Mesh tool preferences](/images/mesh_tool_prefs.png "Mesh tool preferences")

### Shortcuts
Shortcuts for tools in edit mode.

### Selection through
This toggle defines whether the x-ray tools will select through or not. 
The button below allows you to toggle the state of selection through.

For example, you can turn off selection through and x-ray tools will work just like the default blender tools
and set a key to turn it on when it's needed:

<video style="padding-bottom: 20px" controls autoplay muted loop>
  <source src="/videos/mesh_select_through_key_toggle.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>

### Selection frame colors
Setting different colors can be useful to see if selection through is enabled or not if you disabled x-ray shading:

<video style="padding-bottom: 20px" controls autoplay muted loop>
  <source src="/videos/mesh_select_through_color.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>

### Show x-ray shading
When this toggle is turned off, x-ray shading won't automatically turn on in selection through mode:

<video style="padding-bottom: 20px" controls autoplay muted loop>
  <source src="/videos/mesh_select_through_without_xray.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>

### Select all edges and faces
By default, in selection through mode tools select edges that have both their vertices inside the selection region and
faces with their center dot inside the selection region:

<video style="padding-bottom: 20px" controls autoplay muted loop>
  <source src="/videos/mesh_select_edges_faces_default.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>

To select all edges or faces that touch the selection region enable "Select All" toggles (this is slower than the 
default selection on meshes with a lot of geometry):

<video style="padding-bottom: 20px" controls autoplay muted loop>
  <source src="/videos/mesh_select_edges_faces_all.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>

### Directional box and lasso tools
Toggle separate configuration of tool settings for left-to-right and right-to-left directions. For example, you can
set up left-to-right drag direction to select through and right-to-left direction to perform default selection:

<video style="padding-bottom: 20px" controls autoplay muted loop>
  <source src="/videos/mesh_select_direction.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>

### Hide mirror and solidify modifiers
Hide mirror modifier or solidify modifier during selection through and re-enable them after finishing selection. 
This can be useful on dense mesh, making it easier to see real geometry in x-ray shading.

### Show box crosshair or lasso icon 
When you initialize a tool with a keyboard shortcut (for example default B, C, L shortcuts) it displays a starting
indicator - crosshair for box tool and lasso icon for lasso tool: 

![Box crosshair](/images/box_crosshair.png "Box crosshair") ![Lasso icon](/images/lasso_icon.png "Lasso icon")

This toggles can disable them.
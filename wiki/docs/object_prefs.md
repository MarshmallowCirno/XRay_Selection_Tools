#

![Object tool preferences](/images/object_tool_prefs.png "Object tool preferences")

### Shortcuts
Shortcuts for tools in object mode.

### Show x-ray shading
This toggle defines whether the x-ray tools will use x-ray shading or not. 
The button below allows you to toggle the state of x-ray shading.

For example, you can turn off x-ray shading and x-ray tools will work just like the default blender tools
and set a key to turn it on when it's needed:

<video style="padding-bottom: 20px" controls autoplay muted loop>
  <source src="/videos/object_show_xray.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>

### Selection behavior

* In Origin mode you select only objects with origins within the selection region.
* In Contain mode you select only objects entirely enclosed in the selection region:
<video style="padding-bottom: 20px" controls autoplay muted loop>
  <source src="/videos/object_select_contain.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>
* In Overlap mode you select all objects within the selection region, plus any objects
crossing boundaries of the selection region:
<video style="padding-bottom: 20px" controls autoplay muted loop>
  <source src="/videos/object_select_overlap.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>
* In Direction mode you automatically switch between Overlap and Contain selection based on cursor movement direction. 
    * Drag from left to right to select all objects crossing or within the selection region (Overlap).
    * Drag from right to left to select all objects entirely enclosed in the selection region (Contain).

<video style="padding-bottom: 20px" controls autoplay muted loop>
  <source src="/videos/object_select_direction.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>

Note that every mode is slower than the default one on objects with a lot of geometry.

### Show box crosshair or lasso icon 
When you initialize a tool with a keyboard shortcut (for example default B, C, L shortcuts) it displays a starting
indicator - crosshair for box tool and lasso icon for lasso tool: 

![Box crosshair](/images/box_crosshair.png "Box crosshair") ![Lasso icon](/images/lasso_icon.png "Lasso icon")

This toggles can disable them.
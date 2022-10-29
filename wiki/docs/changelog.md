#

## 4.2.5
* Fixed a conflict with addons that use timer (like Hardops or Screencast Keys) that could cause x-ray shading to stop working.

## 4.2.4
* Fixed circle select fallback tools requiring a click to start selection by disabling wait_for_input, copying default blender tool behavior.

## 4.2.3
* Fix for wrong fallback tool keys registration when blender selection is set to right mouse button.
* Changed a couple of labels in addon preferences to be more descriptive.

## 4.2.2
* Fixed bug on releasing circle select in object mode and fallback tool keyitems.

## 4.2.1
* Fixed directory structure and bug on releasing circle selection in mesh mode.

## 4.2.0
* Update to Blender 3.3.1

##  4.1.0
* Box and lasso tool settings for edit mode can be configured separately for left-to-right and right-to-left drag directions.

## 4.0.1
* Fixed shaders in blender fullscreen, added shortcut for toggling addon preferences.

## 4.0.0
* Added contain and overlap selection behavior modes for object tools to addon preferences, similar to autodesk Window/Crossing selection. 
Contain behavior select objects fully contained in the selection region. Overlap behavior selects objects touching and inside the selecting region.
* Added directional behavior for automatically switching between contain and overlap selection mode. 
Drag from left to right to select all objects that are entirely contained in the selection box or lasso, drag from right to left to select all objects that are overlapped by the selection box or lasso.
* Added shortcut configuration for tool selection mode (Set, Extend, Subtract etc.) for individual tools.
* Fixed selection mode buttons in header and properties active tool tab.
* Speed up circle selection in mesh mode.
* Improved drawing of lasso shader.

## 3.1.0
* Added shortcut configuration for tool selection mode (Set, Extend, Subtract etc.) in the addon preferences Advanced Keymap tab.
* Added header buttons in Advanced Keymap to disable/enable addon preinstalled shortcuts. Disabled shortcuts won't be added and won't clutter a blender keyconfig.

## 3.0.1
* Fixed disabling hiding modifiers.

## 3.0.0
* Reworked the addon preference panel, since it used to be confusing.
* Selection through can be toggled by pressing or holding a user-set set button during selection.
* You can set a different color for tools with enabled selection through.
* Implemented selection of all faces and edges in select through mode for lasso select and circle select tools.
* Rewritten code in numpy to improve performance.

## 2.0.14
* Fixed issues with addon registration.
#

## Requirements

* Windows, MacOS or Linux
* Blender 3.3

## How to install

There are two ways to install X-Ray Selection Tools

### From inside Blender

This approach is a bit more convenient, but if you update from an older version of the addon, it leads to a loss of 
previously saved [addon preferences](/mesh_prefs).

![Addon installation](/images/addon_install.png "Addon installation")
_installation from the Addons tab of Blender's preferences, by selecting the addon's .zip file_

### Using the System's File Browser

The approach is recommended, especially if you update from an older version to a newer one, as all previous addon 
preferences will be kept.

![Addon archive](/images/addon_archive.png "Addon archive") _with Blender closed, find your downloaded .zip file_

![Addon extraction](/images/addon_extracted.png "Addon extraction") _extract it, you need the `space_view3d_xray_selection_tools` folder_

![Addon structure](/images/addon_structure.png "Addon structure") _it contains the `__init__.py` file_

![Placing addon folder](/images/addon_placed.png "Placing addon folder") _place the addon folder to Blender's addons directory_

!!! danger "Attention"

    If you have a pre-existing `space_view3d_xray_selection_tools` folder in the addons directory, remove it first, 
    before pasting the new version!

!!! info "Blender's Addons Directory"

    **Linux:** `/home/name/.config/blender/3.3/scripts/addons`  
    **MacOS:** `/Users/name/Library/Application Support/Blender/3.3/scripts/addons`  
    **Windows:** `C:\Users\name\AppData\Roaming\Blender Foundation\Blender\3.3\scripts\addons`  

    Depending on your Blender version, replace `3.3` accordingly.

![Addon search](/images/addon_search.png "Addon search") _start Blender, open the preferences, switch to the Addons tab and search for x-ray_

![Addon activation](/images/addon_activate.png "Addon activation") _activate X-Ray Selection Tools and unfold the [addon preferences](/mesh_prefs)_

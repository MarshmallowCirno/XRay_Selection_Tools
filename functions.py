import bpy, bmesh
from bpy_extras.view3d_utils import location_3d_to_region_2d


def get_2d_co(region, rv3d, ob, co):
    '''Get 2D coordinates of point'''
    co_world = ob.matrix_world @ co
    co_2d = location_3d_to_region_2d(region, rv3d, co_world)
    return co_2d
    
    
def co_inside_rectangle(co, xmin, xmax, ymin, ymax):
    '''Check if the point is inside the rectangle'''
    if co[0] < xmin:
        return False
    if co[0] > xmax:
        return False
    if co[1] < ymin:
        return False
    if co[1] > ymax:
        return False
    return True
    
    
def co_inside_poly(co, poly):
    '''Check if the point is inside the polygon'''
    # simple bounding box test
    # check if co completely outside of the bounding box
    xlist = [p[0] for p in poly]
    ylist = [p[1] for p in poly]
    
    xmin = min(xlist)
    xmax = max(xlist)
    ymin = min(ylist)
    ymax = max(ylist)
    
    if not co_inside_rectangle(co, xmin, xmax, ymin, ymax):
        return False

    # https://en.wikipedia.org/wiki/Even–odd_rule
    num = len(poly)
    i = 0
    j = num - 1
    inside = False
    for i in range(num):
        if ((poly[i][1] > co[1]) != (poly[j][1] > co[1])) and \
                (co[0] < poly[i][0] + (poly[j][0] - poly[i][0]) * (co[1] - poly[i][1]) /
                                  (poly[j][1] - poly[i][1])):
            inside = not inside
        j = i
    return inside
    
    
def segment_intersect_rectangle(v1, v2, xmin, xmax, ymin, ymax):
    # https://github.com/dfelinto/blender/blob/master/source/blender/editors/space_view3d/view3d_select.c

    # check if the points are completely outside the rectangle, both laying outside of one of its side
    if v1[0] < xmin and v2[0] < xmin:
        return False
    if v1[0] > xmax and v2[0] > xmax:
        return False
    if v1[1] < ymin and v2[1] < ymin:
        return False
    if v1[1] > ymax and v2[1] > ymax:
        return False

    # simple check for lines intersecting
    d1 = (v1[1] - v2[1]) * (v1[0] - xmin) + (v2[0] - v1[0]) * (v1[1] - ymin)
    d2 = (v1[1] - v2[1]) * (v1[0] - xmin) + (v2[0] - v1[0]) * (v1[1] - ymax)
    d3 = (v1[1] - v2[1]) * (v1[0] - xmax) + (v2[0] - v1[0]) * (v1[1] - ymax)
    d4 = (v1[1] - v2[1]) * (v1[0] - xmax) + (v2[0] - v1[0]) * (v1[1] - ymin)

    if (d1 < 0 and d2 < 0 and d3 < 0 and d4 < 0):
        return False
    if (d1 > 0 and d2 > 0 and d3 > 0 and d4 > 0):
        return False                
    return True
    
    
def select_elems_in_rectangle(context, mode, xmin, xmax, ymin, ymax, select_all_edges, select_all_faces):
    region = context.region
    rv3d = context.region_data

    def create_vert_dictionary():
        '''Create vert dictionary {vert: {"co":co, "inside":inside})'''
        vert_dict = {}
        for vert in bm.verts:
            if not vert.hide: # if vertex is hidden then faces and edges that it defines would be hidden to. so its co isn't needed
                co = get_2d_co(region, rv3d, ob, vert.co)
                if co is not None:
                    inside = co_inside_rectangle(co, xmin, xmax, ymin, ymax)
                else:
                    inside = False
                vert_dict[vert] = {"co":co, "inside":inside}
        return vert_dict
            
    def do_elem_selection(elems):
        if mode == 'SET':
            for elem in elems:
                elem.select = elem.tag
                elem.tag = False
        elif mode == 'ADD':
            for elem in elems:
                if elem.tag:
                    elem.select = True
                    elem.tag = False
        elif mode == 'SUB':
            for elem in elems:
               if elem.tag:
                    elem.select = False
                    elem.tag = False
        elif mode == 'XOR':
            for elem in elems:
                if elem.tag:
                    elem.select = not elem.select
                    elem.tag = False
        elif mode == 'AND':
            for elem in elems:
                if not elem.tag:
                    elem.select = False
                else:
                    elem.tag = False
                    
    # main loop
    for ob in context.selected_objects:
        if ob.type == 'MESH':
            me = ob.data
            bm = bmesh.from_edit_mesh(me)

            vert_dict = create_vert_dictionary()
            
            if context.tool_settings.mesh_select_mode[0]: 
                # select vertices which coordinates are inside the selection rectangle
                for vert, vals in vert_dict.items():
                    if vals["co"] is None or vals["inside"] == False:
                        continue
                    # tag found vert for selection op
                    vert.tag = True
                    
                do_elem_selection(bm.verts)

            if context.tool_settings.mesh_select_mode[1]:
                # try to select edges that are completely inside the selection rectangle
                if not select_all_edges:  
                    found_inner_edges = False
                    for edge in bm.edges:
                        if not edge.hide:
                            # get 2d coordinates of edge vertices 
                            # skip edge if one of the edge vertices is behind the origin of a perspective view and coordinates can't be calculated
                            # or one of the vert coordinates is outside the selection box
                            v1 = vert_dict[edge.verts[0]]
                            if v1["co"] is None or v1["inside"] == False:
                                continue
                            v2 = vert_dict[edge.verts[1]]
                            if v2["co"] is None or v1["inside"] == False:
                                continue
                            # tag found edge for selection op
                            edge.tag = True
                            found_inner_edges = True
                            
                # select all edges that intersect the selection rectangle
                if select_all_edges or (not select_all_edges and found_inner_edges == False):
                    for edge in bm.edges:
                        if not edge.hide:
                            # skip selection op for already selected edges
                            if not edge.tag:
                                # get 2d coordinates of edge vertices 
                                v1 = vert_dict[edge.verts[0]]
                                v2 = vert_dict[edge.verts[1]]
                                # tag edge for selection if one of the vert coordinates is inside the selection box
                                if v1["inside"] == True or v1["inside"] == True:
                                    edge.tag = True
                                # skip edge if one of the edge vertices is behind the origin of a perspective view and coordinates can't be calculated
                                elif v1["co"] is None or v2["co"] is None:
                                    continue
                                # check if the edge intersects the selection rectangle
                                elif segment_intersect_rectangle(v1["co"], v2["co"], xmin, xmax, ymin, ymax):
                                    edge.tag = True

                do_elem_selection(bm.edges)

            if context.tool_settings.mesh_select_mode[2]:
                # select faces which centers are inside the selection rectangle
                if not select_all_faces:
                    for face in bm.faces:
                        if not face.hide:
                            center = get_2d_co(region, rv3d, ob, face.calc_center_median())
                            if co_inside_rectangle(center, xmin, xmax, ymin, ymax):
                                face.tag = True
                else:
                    # select faces which edges intersect the selection rectangle
                    for edge in bm.edges:
                        if not edge.hide:
                            # get 2d coordinates of edge vertices 
                            # skip edge if one of edge vertices is behind the origin of a perspective view and coordinates can't be calculated
                            v1 = vert_dict[edge.verts[0]]
                            if v1["co"] is None:
                                continue
                            v2 = vert_dict[edge.verts[1]]
                            if v2["co"] is None:
                                continue
                            # check if the edge intersects the selection rectangle or one of verts are inside the rectangle
                            if v1["inside"] or v2["inside"] or segment_intersect_rectangle(v1["co"], v2["co"], xmin, xmax, ymin, ymax):
                                # if intersects, then select all nearby faces 
                                for face in edge.link_faces:
                                    if not face.tag and not face.hide:
                                        #tag the face for selection op and to exclude from the second selection pass
                                        face.tag = True
                            
                    # select faces that have the selection rectangle inside its area
                    for face in bm.faces:
                        if not face.hide:
                            # skip selection op for already selected faces
                            if not face.tag:
                                # check if selection rectangle vert is outside of the face bounding box
                                poly = [vert_dict[vert]["co"] for vert in face.verts if vert_dict[vert]["co"] is not None]
                                if co_inside_poly((xmin, ymin), poly):
                                    #tag the face for selection op
                                    face.tag = True
                                    
                do_elem_selection(bm.faces)

            # flush face selection after selecting/deselecting edges and vertices
            bm.select_flush_mode()
                                    
            # to do
            # numpy https://blender.stackexchange.com/questions/6155/how-to-convert-coordinates-from-vertex-to-world-space
            # https://blenderartists.org/t/efficient-copying-of-vertex-coords-to-and-from-numpy-arrays/661467/8
            
            bmesh.update_edit_mesh(me, loop_triangles=False, destructive=False) 
            
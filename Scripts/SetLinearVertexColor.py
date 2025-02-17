import maya.cmds as cmds
import maya.api.OpenMaya as om
import pathlib
import maya.mel as mel

# Used to store the names of the generated locators
created_locators = []
start_locator = None
end_locator = None

# Get the lowest and highest points of the bbox of the selected object
def get_bbox_corners(mesh_name):
    # Get the MObject of the object
    selectionList = om.MSelectionList()
    selectionList.add(mesh_name)
    m_dag_path = selectionList.getDagPath(0)
    m_object = m_dag_path.node()
    # Apply the transform of the object to the bbox to get the aabb
    m_fn_transform = om.MFnTransform(m_dag_path)
    m_matrix = m_fn_transform.transformation().asMatrix()
    # Get the lowest and highest points of the bbox center
    m_fn_mesh = om.MFnMesh(m_dag_path)
    bbox = m_fn_mesh.boundingBox
    bbox_center_min = om.MVector(bbox.center.x, bbox.min.y, bbox.center.z)
    bbox_center_max = om.MVector(bbox.center.x, bbox.max.y, bbox.center.z)
    bbox_center_min = convert_distance(bbox_center_min * m_matrix)
    bbox_center_max = convert_distance(bbox_center_max * m_matrix)
    return om.MPoint(bbox_center_min), om.MPoint(bbox_center_max)

# Create a locator and place it at the specified position
def create_locator_at_position(position, name):
    locator_name = cmds.spaceLocator(name=name)[0]
    cmds.xform(locator_name, t=(position[0], position[1], position[2]))
    created_locators.append(locator_name)
    return locator_name

# Select mesh and fill it into the textField
def select_mesh(mesh_field):
    selected = cmds.ls(selection=True, type='transform')
    if selected:
        try:
            generate_locators(selected[0])
            cmds.textFieldButtonGrp(mesh_field, edit=True, text=selected[0])
            #select the mesh
            cmds.select(selected[0])
        except:
            cmds.warning("Please a mesh object")
            return 
            
# Generate locators
def generate_locators(mesh_name):
    global start_locator, end_locator
    if mesh_name:
        min_point, max_point = get_bbox_corners(mesh_name)
        # Create locators and place them at the lowest and highest points of the bbox
        if (start_locator is None) and (end_locator is None):
            start_locator = create_locator_at_position((min_point.x, min_point.y, min_point.z), "StartLoc")
            end_locator = create_locator_at_position((max_point.x, max_point.y, max_point.z), "EndLoc")
        else:
            cmds.xform(start_locator, t=(min_point.x, min_point.y, min_point.z))
            cmds.xform(end_locator, t=(max_point.x, max_point.y, max_point.z))
        cmds.confirmDialog(title="Success", message="Locators are set", button=["OK"])
    else:
        cmds.confirmDialog(title="Failure", message="Locators are missing. Please restart the script", button=["OK"])

# Delete all generated locators
def delete_locators_on_close():
    if created_locators:
        for locator in created_locators:
            if cmds.objExists(locator):
                cmds.delete(locator)
        created_locators.clear()

# Generate vertex colors
def generate_vertex_colors():
    if start_locator and end_locator:
        mesh_name = cmds.textFieldButtonGrp("SelectedMesh", q=True, text=True)
        # Set the initial color and color display settings
        cmds.polyColorPerVertex(rgb=(0, 0, 0))
        cmds.setAttr(mesh_name + '.displayColors', 1)
        # Get the positions of the locators
        start_pos = cmds.xform(start_locator, query=True, t=True, worldSpace=True)
        end_pos =  cmds.xform(end_locator, query=True, t=True, worldSpace=True)
        # Use MVector to represent the positions
        start_vec = om.MVector(start_pos[0], start_pos[1], start_pos[2])
        end_vec = om.MVector(end_pos[0], end_pos[1], end_pos[2])
        print(start_vec)
        print(end_vec)
        # Calculate the direction vector (end - start)
        direction_vec = end_vec - start_vec
        direction_vec_length = direction_vec.length()
        direction_vec = direction_vec.normal()
        # Get the MFnMesh object
        # try to get the mesh vertex component
        # if not, add the mesh to the selection list
        selectionList = om.MGlobal.getActiveSelectionList()
        dagPath, component = selectionList.getComponent(0)
        if component.apiType() != om.MFn.kMeshVertComponent:
            if selectionList.isEmpty():
                selectionList.add(mesh_name)
            if dagPath.partialPathName() is not mesh_name:
                selectionList.clear()
                selectionList.add(mesh_name)
        dagPath, component = selectionList.getComponent(0)
        fn_mesh = om.MFnMesh(dagPath)
        itVtx = om.MItMeshVertex(dagPath, component)
        # Iterate through each vertex, calculate the projection percentage, and set the vertex color
        colors = []
        vertexIds = []
        while not itVtx.isDone():
            # Calculate the vector from the vertex to the start_locator
            vertex_loc = convert_distance_openMaya(om.MVector(itVtx.position(om.MSpace.kWorld)))
            vertex_vec = vertex_loc - start_vec
            # Calculate the dot product of the vertex vector and the direction vector
            dot_product = vertex_vec * direction_vec
            # Calculate the projection percentage (clamp between 0 and 1)
            percentage = dot_product / direction_vec_length
            percentage = max(0, min(1, percentage))  # Clamp the percentage between 0 and 1
            # Calculate the vertex color: gradient based on the percentage
            startCol = om.MColor(cmds.colorSliderGrp('StartColor', q=True, rgb=True))
            endCol = om.MColor(cmds.colorSliderGrp('EndColor', q=True, rgb=True))
            finalCol = startCol * (1 - percentage) + endCol * percentage
            colors.append(finalCol)
            vertexIds.append(itVtx.index())
            itVtx.next()
        # Set the calculated colors as vertex colors
        print(len(vertexIds))
        fn_mesh.setVertexColors(colors, vertexIds)
        cmds.confirmDialog(title="Success", message="Vertex colors generated!", button=["OK"])
    else:
        cmds.confirmDialog(title="Failure", message="Lose Locators", button=["OK"])

# select the texture path
def select_texture_path():
    singleFilter = "png(*.png)"
    texture_path = cmds.fileDialog2(fileMode=0, caption="Save As",fileFilter=singleFilter,dialogStyle=2)
    return texture_path
    
# Bake color texture
def bake_color_texture():
    texture_path = select_texture_path()[0]
    texture_size = cmds.intFieldGrp('TextureSize', q=True, v=True)[0]
    print("bake in "+texture_path+" size:"+str(texture_size))
    mel.eval("PaintVertexColorToolOptions;")
    cmds.artAttrPaintVertexCtx(cmds.currentCtx(),e=True,esf=texture_path,fsx=texture_size,fsy=texture_size)
    return

def convert_distance_openMaya(length):
    unit = cmds.currentUnit(q=True,linear=True)
    if(unit == "cm"):
        return length
    elif(unit == "m" or unit == "meter"):
        return length*0.01

# Window interface
def create_window():
    if cmds.window("bboxWindow", exists=True):
        cmds.deleteUI("bboxWindow", window=True)
    window = cmds.window("bboxWindow", title="Set Linear Vertex Color")
    cmds.columnLayout(adjustableColumn=True)
    # Create a button to select the mesh
    cmds.text(label="Select A Mesh", font="boldLabelFont")
    mesh_field = cmds.textFieldButtonGrp("SelectedMesh", label="Mesh", buttonLabel="Select", cw=[1, 60], buttonCommand=lambda: select_mesh(mesh_field))
    # Create color transition
    cmds.colorSliderGrp('StartColor', label='StartColor', cw=[1, 60], rgb=(0, 0, 0))
    cmds.floatSliderGrp('StartAlpha', label="StartAlpha", cw=[1, 60], f=True, min=0, max=1, v=1)
    cmds.colorSliderGrp('EndColor', label='EndColor', cw=[1, 60], rgb=(1, 1, 1))
    cmds.floatSliderGrp('EndAlpha', label="EndAlpha", cw=[1, 60], f=True, min=0, max=1, v=1)
    # Create a button to generate vertex colors
    cmds.button(label="Set Vertex Color", command=lambda x: generate_vertex_colors())
    # Set texture Size/ Default is 512
    cmds.intFieldGrp('TextureSize', label="Texture Size", cw=[1, 60], v=[512,512,1024,2048])
    # Create a button to bake color texture .png
    cmds.button(label="Bake into PNG", command=lambda x: bake_color_texture())
    # Set the callback when the window is closed 
    cmds.window(window, edit=True, closeCommand=delete_locators_on_close)
    cmds.showWindow("bboxWindow")

# Run the window
create_window()
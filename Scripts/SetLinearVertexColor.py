import maya.cmds as cmds
import maya.api.OpenMaya as om
# 用于存储生成的locator的名称
created_locators = []
start_locator = None
end_locator = None
# 获取选中的物体的bbox最低点和最高点
def get_bbox_corners(mesh_name):
    # 获取物体的MObject
    selectionList = om.MSelectionList()
    selectionList.add(mesh_name)
    m_dag_path = selectionList.getDagPath(0)
    m_object = m_dag_path.node()
    # 获取物体的transform应用到bbox上变成aabb
    m_fn_transform = om.MFnTransform(m_dag_path)
    m_matrix = m_fn_transform.transformation().asMatrix()
    # 获取bbox的中心最低点和最高点
    m_fn_mesh = om.MFnMesh(m_dag_path)
    bbox = m_fn_mesh.boundingBox
    bbox_center_min = om.MVector(bbox.center.x,bbox.min.y,bbox.center.z)
    bbox_center_max = om.MVector(bbox.center.x,bbox.max.y,bbox.center.z)
    bbox_center_min = bbox_center_min * m_matrix
    bbox_center_max = bbox_center_max * m_matrix
    return om.MPoint(bbox_center_min), om.MPoint(bbox_center_max)
# 创建locator并放置在指定位置
def create_locator_at_position(position,name):
    locator_name = cmds.spaceLocator(name=name)[0]
    cmds.xform(locator_name, t=(position[0], position[1], position[2]))
    created_locators.append(locator_name)
    return locator_name

# 选择mesh并填充到textField中
def select_mesh(mesh_field):
    selected = cmds.ls(selection=True, type='transform')
    if selected:
        cmds.textFieldButtonGrp(mesh_field, edit=True, text=selected[0])
        generate_locators(mesh_field)
        
# 生成locator
def generate_locators(mesh_field):
    global start_locator, end_locator
    mesh_name = cmds.textFieldButtonGrp(mesh_field, query=True, text=True)
    if mesh_name:
        min_point, max_point = get_bbox_corners(mesh_name)
        # 创建locator并放置在bbox的最低点和最高点
        if (start_locator is None) and (end_locator is None):
            start_locator = create_locator_at_position((min_point.x, min_point.y, min_point.z),"StartLoc")
            end_locator = create_locator_at_position((max_point.x, max_point.y, max_point.z),"EndLoc")
        else:
            cmds.xform(start_locator, t=(min_point.x, min_point.y, min_point.z))
            cmds.xform(end_locator, t=(max_point.x, max_point.y, max_point.z))
        cmds.confirmDialog(title="Success", message="Locators are set！", button=["OK"])
    else:
        cmds.confirmDialog(title="Failure", message="Select A Mesh！", button=["OK"])
# 删除所有生成的locator
def delete_locators_on_close():
    if created_locators:
        for locator in created_locators:
            if cmds.objExists(locator):
                cmds.delete(locator)
        created_locators.clear() 
# 生成顶点色
def generate_vertex_colors():
    if start_locator and end_locator:
        # 获取locator的位置
        start_pos = cmds.xform(start_locator, query=True, t=True, worldSpace=True)
        end_pos = cmds.xform(end_locator, query=True, t=True, worldSpace=True)
        # 使用MVector来表示位置
        start_vec = om.MVector(start_pos[0], start_pos[1], start_pos[2])
        end_vec = om.MVector(end_pos[0], end_pos[1], end_pos[2])
        # 计算方向向量 (end - start)
        direction_vec = end_vec - start_vec
        direction_vec_length = direction_vec.length()
        direction_vec = direction_vec.normal()
        # 获取MFnMesh对象
        selectionList = om.MGlobal.getActiveSelectionList()
        mesh_name = cmds.textFieldButtonGrp("SelectedMesh",q=True,text=True)
        if selectionList.isEmpty():
            selectionList.add(mesh_name)
        dagPath,component = selectionList.getComponent(0)
        fn_mesh = om.MFnMesh(dagPath)
        itVtx = om.MItMeshVertex(dagPath,component)
        # 遍历每个顶点，计算投射百分比并设置顶点颜色
        colors = []
        vertexIds = []
        # 设置初始颜色和颜色显示设置
        cmds.polyColorPerVertex(rgb=(0,0,0))
        cmds.setAttr(mesh_name+'.displayColors',1)
        while itVtx.isDone() is False:
            # 计算顶点到start_locator的向量
            vertex_vec = om.MVector(itVtx.position(om2.MSpace.kWorld)) - start_vec
            # 计算顶点向量和方向向量的点积
            dot_product = vertex_vec * direction_vec
            # 计算投射百分比 (限制在0到1之间)
            percentage = dot_product/direction_vec_length
            percentage = max(0, min(1, percentage))  # 限制百分比在0到1之间
            # 计算顶点色：根据百分比渐变
            startCol = om.MColor(cmds.colorSliderGrp('StartColor',q=True,rgb=True))
            endCol = om.MColor(cmds.colorSliderGrp('EndColor',q=True,rgb=True))
            finalCol = startCol*(1-percentage)+endCol*percentage
            colors.append(finalCol)
            vertexIds.append(itVtx.index())
            itVtx.next()
        # 将计算出的颜色设置为顶点色
        print(len(vertexIds))
        fn_mesh.setVertexColors(colors,vertexIds)
        cmds.confirmDialog(title="Success", message="顶点色生成完毕！", button=["OK"])
    else:
        cmds.confirmDialog(title="Failure", message="请先生成Locator！", button=["OK"])
        
# 窗口界面
def create_window():
    if cmds.window("bboxWindow", exists=True):
        cmds.deleteUI("bboxWindow", window=True)
    window = cmds.window("bboxWindow", title="Set Linear Vertex Color")
    cmds.columnLayout(adjustableColumn=True)
    # 创建选择mesh的按钮
    cmds.text(label="Select A Mesh",font="boldLabelFont")
    mesh_field = cmds.textFieldButtonGrp("SelectedMesh",label="Mesh", buttonLabel="Select", cw=[1,60], buttonCommand=lambda: select_mesh(mesh_field))
    # 创建颜色过渡
    cmds.colorSliderGrp('StartColor',label='StartColor', cw=[1,60],rgb=(0, 0, 0) )
    cmds.floatSliderGrp('StartAlpha',label="StartAlpha", cw=[1,60],f=True,min=0,max=1,v=1)
    cmds.colorSliderGrp('EndColor', label='EndColor', cw=[1,60], rgb=(1, 1, 1) )
    cmds.floatSliderGrp('EndAlpha',label="EndAlpha", cw=[1,60],f=True,min=0,max=1,v=1)
    # 创建生成顶点色按钮
    cmds.button(label="Set", command=lambda x: generate_vertex_colors())
    # 设置窗口关闭时的回调
    cmds.window(window, edit=True, closeCommand=delete_locators_on_close)
    cmds.showWindow("bboxWindow")
# 运行窗口
create_window()
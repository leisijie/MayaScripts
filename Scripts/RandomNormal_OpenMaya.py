import maya.cmds as cmds
import maya.api.OpenMaya as om
import os
import random
import math
import datetime

class RandomNormal(object): 
    def __init__(self):
        if cmds.window("vertexColorWindow", exists=True):
            cmds.deleteUI("vertexColorWindow", window=True)
        window = cmds.window("vertexColorWindow", title="Vertex Color Tool", widthHeight=(300, 200))
        cmds.columnLayout(adjustableColumn=True)
        
        cmds.rowLayout(adjustableColumn=1,numberOfColumns=2)
        self.slider = cmds.floatSliderGrp(label = "MaxAngle",field=True,min=0,max=180,value=10)
        cmds.button(label="Exec", command=self.random_normal)
        cmds.setParent("..")
        
        cmds.separator(style="none", height=10)
        cmds.button(label="Use Maya Normals",command=self.use_maya_normals)
        cmds.button(label="Add Color Set",command=self.add_color_set_for_all_mesh)
        cmds.showWindow(window)
        
    def random_normal(self,arg):
        # 记录开始时间
        start_time = datetime.datetime.now()
        # 计算最大角度
        maxAngle = cmds.floatSliderGrp(self.slider,q=True,v=True)/180.0
        # 获取当前选择的物体
        selection_list = om.MGlobal.getActiveSelectionList()
        selection_list_iter = om.MItSelectionList(selection_list)
        
        while not selection_list_iter.isDone():
            print(selection_list_iter.getDagPath())
            cmds.polySetToFaceNormal( setUserNormal=True )
            # 获取当前选择物体的路径
            dag_path = selection_list_iter.getDagPath()
            # 
            try:
                mesh_fn = om.MFnMesh(dag_path)
            except:
                cmds.warning("Please select a mesh")
                selection_list_iter.next()
                continue
            tangents = mesh_fn.getTangents()
            
            face_iter = om.MItMeshPolygon(dag_path)
            while not face_iter.isDone():
               vertex_ids = face_iter.getVertices()
               face_id = face_iter.index()
               face_ids = [face_id] * len(vertex_ids)
               
               #获取normal/tangent/binormal
               normal_old = face_iter.getNormal()
               
               tangent_id = face_iter.tangentIndex(0)
               tangent = om.MVector(tangents[tangent_id])
               
               binormal = (normal_old ^ tangent).normal()
               
               #计算新的Normal
               phi = random.random() * math.pi * maxAngle
               theta = random.random() * math.pi * 2
               # 随机向量
               random_vector = om.MVector(math.cos(theta) * math.sin(phi), math.sin(theta) * math.sin(phi), math.cos(phi)).normal()
               normal_new = (binormal  * random_vector.x + tangent * random_vector.y + normal_old * random_vector.z).normal();
               normal_news = [normal_new] * len(vertex_ids)
               #设置新的Normal
               mesh_fn.setFaceVertexNormals(normal_news,face_ids,vertex_ids)
               
               face_iter.next()
            #获取结束时间
            end_time = datetime.datetime.now()
            cmds.warning("cost total time: %s second"%(end_time - start_time))
            selection_list_iter.next()
            
    def traverse_outliner_hierarchy(self,parent_item, transform_set, depth=0):
        # 获取当前项的类型
        item_type = cmds.objectType(parent_item)
        
        # 如果是 mesh，则将其添加到列表中
        if item_type == "mesh":
            names = parent_item.split("|")
            name_last_index = -1-len(names[-1])
            name = parent_item[:name_last_index]
            transform_set.add(name)
        
        # 获取子项列表
        children = cmds.listRelatives(parent_item, children=True, fullPath=True) or []
        
        # 遍历子项
        for child in children:
            # 递归遍历子项的子项
            self.traverse_outliner_hierarchy(child, transform_set, depth + 1)

    def get_outliner_transforms(self):
        # 获取 Outliner 中的顶层项列表
        top_level_items = cmds.ls(assemblies=True)
        
        # 用于存储 Transform 的列表
        transform_set = set()
        
        # 遍历顶层项
        for item in top_level_items:
            # 获取 Outliner 中的 Transform
            self.traverse_outliner_hierarchy(item, transform_set)

        # 返回 Transform 列表
        return transform_set
    
    def add_color_set_for_all_mesh(self,arg):
        #选择所有Mesh Object
        transform_set = self.get_outliner_transforms()
        cmds.select(transform_set)
        #OpenMaya
        selection_list = om.MGlobal.getActiveSelectionList()
        selection_list_iter = om.MItSelectionList(selection_list)
        #循环添加Color Set
        while not selection_list_iter.isDone():
            # 获取当前选择物体的路径
            dag_path = selection_list_iter.getDagPath()
            mesh_fn = om.MFnMesh(dag_path)
            #如果没有Color Set则添加一个 
            if(mesh_fn.numColorSets<=0):
                mesh_fn.createColorSet("ColorSet0",True)
            selection_list_iter.next()
    
    def use_maya_normals(self,arg):
        #选择所有Mesh Object
        transform_set = self.get_outliner_transforms()
        cmds.select(transform_set)
        shapes = cmds.ls(selection=True, dagObjects=True, noIntermediate=True, type='mesh')
        for shape in shapes:
            if not cmds.objExists(shape + '.UseMayaNormals'):
                cmds.addAttr(shape, longName='UseMayaNormals', attributeType='bool')
            cmds.setAttr(shape + '.UseMayaNormals', channelBox=True, lock=False)
            cmds.setAttr(shape + '.UseMayaNormals', 1)
            print(shape + ' hard edge export is now active')
            
####____MAIN_____####
random_W = RandomNormal()
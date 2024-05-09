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
        self.slider = cmds.floatSliderGrp(label = "MaxAngle",field=True,min=0,max=180,value=10)
        cmds.button(label="Exec", command=self.random_normal)
        cmds.button(label="Use Maya Normals",command=self.use_maya_normals)
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
            cmds.warning("Total time: %s second"%(end_time - start_time))
            selection_list_iter.next()
    
    def use_maya_normals(self,arg):
        shapes = cmds.ls(selection=True, dagObjects=True, noIntermediate=True, type='mesh')
        for shape in shapes:
            if not cmds.objExists(shape + '.UseMayaNormals'):
                cmds.addAttr(shape, longName='UseMayaNormals', attributeType='bool')
            cmds.setAttr(shape + '.UseMayaNormals', channelBox=True, lock=False)
            cmds.setAttr(shape + '.UseMayaNormals', 1)
            print(shape + ' hard edge export is now active')
        
random_W = RandomNormal()
import maya.cmds as cmds
import maya.api.OpenMaya as om
import random
import math
import datetime

class RandomNormal(object): 
    def __init__(self):
        if cmds.window("SetFaceRandomNormal", exists=True):
            cmds.deleteUI("SetFaceRandomNormal", window=True)
        window = cmds.window("SetFaceRandomNormal", title="SetFaceRandomNormal", widthHeight=(500, 10))
        cmds.columnLayout(adjustableColumn=True)
        
        cmds.rowLayout(adjustableColumn=1,numberOfColumns=2)
        self.slider = cmds.floatSliderGrp(label = "MaxAngle",field=True,cal=[1,"left"],min=0,max=180,value=10)
        cmds.button(label="Exec", command=self.random_normal)
        cmds.setParent("..")
        
        cmds.separator(style="none", height=10)
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
            cmds.polySetToFaceNormal( setUserNormal=True )
            # 获取当前选择物体的路径
            dag_path,component = selection_list_iter.getComponent()
            # 
            try:
                mesh_fn = om.MFnMesh(dag_path)
            except:
                cmds.warning("Please select a mesh")
                selection_list_iter.next()
                continue
            tangents = mesh_fn.getTangents()
            
            face_iter = om.MItMeshPolygon(dag_path,component)
            face_ids=[]
            vertex_ids=[]
            normals=[]
            while not face_iter.isDone():
                m_vertex_ids = face_iter.getVertices()
                vertex_ids += m_vertex_ids
                face_id = face_iter.index()
                face_ids += [face_id] * len(m_vertex_ids)

                #获取normal/tangent/binormal
                normal_old = face_iter.getNormal()

                tangent_id = face_iter.tangentIndex(0)
                tangent = om.MVector(tangents[tangent_id])

                binormal = (normal_old ^ tangent).normal()

                #计算新的Normal偏移方向
                phi = random.random() * math.pi * maxAngle
                theta = random.random() * math.pi * 2
                # 随机向量
                random_vector = om.MVector(math.cos(theta) * math.sin(phi), math.sin(theta) * math.sin(phi), math.cos(phi)).normal()
                normal_new = (binormal  * random_vector.x + tangent * random_vector.y + normal_old * random_vector.z).normal();
                normals += [normal_new] * len(m_vertex_ids)

                face_iter.next()
            #设置新的Normal
            mesh_fn.setFaceVertexNormals(normals,face_ids,vertex_ids,om.MSpace.kWorld)
            #获取结束时间
            end_time = datetime.datetime.now()
            cmds.warning("cost total time: %s second"%(end_time - start_time))
            selection_list_iter.next()
            
####____MAIN_____####
random_W = RandomNormal()
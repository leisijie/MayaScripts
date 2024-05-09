import maya.cmds as cmds
import maya.OpenMaya as om
import random
import math

def print_face_vertices(arg):
    # 获取当前选择的物体
    selection = cmds.ls(selection=True, type='transform')
    
    if not selection:
        print("请选择一个物体")
        return
    
    # 遍历所选物体
    for obj in selection:
        cmds.polySetToFaceNormal( setUserNormal=True )
        # 获取物体的所有面
        faces = cmds.ls(obj + '.f[*]', flatten=True)
        
        # 遍历每个面
        for face in faces:
            # 获取面的所有顶点
            vertices = cmds.ls(cmds.polyListComponentConversion(face, fromFace=True, toVertexFace=True), flatten=True)
            
            vertex = vertices[0]
            # 获取顶点的法线
            normal_raw = cmds.polyNormalPerVertex(vertex, query=True, xyz=True)
            normal = om.MVector(normal_raw[0],normal_raw[1],normal_raw[2]).normal()
            # 获取顶点的切线
            pos_1 = cmds.xform(vertex,ws = True,translation=True,q=True)
            pos1 = om.MVector(pos_1[0],pos_1[1],pos_1[2])
            pos_2 = cmds.xform(vertices[-1],ws=True,translation=True,q=True)
            pos2 = om.MVector(pos_2[0],pos_2[1],pos_2[2])
            tangent = (pos2 - pos1).normal();
            # 获取顶点的副法线
            binormal = (normal^tangent).normal()
            # 随机角度
            phi = random.random() * math.pi * 0.3
            theta = random.random() * math.pi * 2
            # 随机向量
            random_vector = om.MVector(math.cos(theta) * math.sin(phi), math.sin(theta) * math.sin(phi), math.cos(phi)).normal()
            random_vector = (binormal  * random_vector.x + tangent * random_vector.y + normal * random_vector.z).normal();
            new_normal = (random_vector.x, random_vector.y, random_vector.z)
            
            # 遍历每个顶点
            for vertex in vertices:
                cmds.polyNormalPerVertex(vertex, xyz=new_normal)

def show_window():
    window = cmds.window("RandomNormal", title="Random Normal Tool", widthHeight=(300, 200))
    cmds.columnLayout(adj = True, cal='right')
    cmds.floatSliderGrp(label = "MaxDistance",field=True,min=0.01,max=100,value=10,dc=print_face_vertices)
    cmds.button(label="Random",command=print_face_vertices)
    cmds.showWindow()
# 调用函数
show_window()

import maya.cmds as cmds
import maya.OpenMaya as om
import random
import math

def print_face_vertices(arg):
    # ��ȡ��ǰѡ�������
    selection = cmds.ls(selection=True, type='transform')
    
    if not selection:
        print("��ѡ��һ������")
        return
    
    # ������ѡ����
    for obj in selection:
        cmds.polySetToFaceNormal( setUserNormal=True )
        # ��ȡ�����������
        faces = cmds.ls(obj + '.f[*]', flatten=True)
        
        # ����ÿ����
        for face in faces:
            # ��ȡ������ж���
            vertices = cmds.ls(cmds.polyListComponentConversion(face, fromFace=True, toVertexFace=True), flatten=True)
            
            vertex = vertices[0]
            # ��ȡ����ķ���
            normal_raw = cmds.polyNormalPerVertex(vertex, query=True, xyz=True)
            normal = om.MVector(normal_raw[0],normal_raw[1],normal_raw[2]).normal()
            # ��ȡ���������
            pos_1 = cmds.xform(vertex,ws = True,translation=True,q=True)
            pos1 = om.MVector(pos_1[0],pos_1[1],pos_1[2])
            pos_2 = cmds.xform(vertices[-1],ws=True,translation=True,q=True)
            pos2 = om.MVector(pos_2[0],pos_2[1],pos_2[2])
            tangent = (pos2 - pos1).normal();
            # ��ȡ����ĸ�����
            binormal = (normal^tangent).normal()
            # ����Ƕ�
            phi = random.random() * math.pi * 0.3
            theta = random.random() * math.pi * 2
            # �������
            random_vector = om.MVector(math.cos(theta) * math.sin(phi), math.sin(theta) * math.sin(phi), math.cos(phi)).normal()
            random_vector = (binormal  * random_vector.x + tangent * random_vector.y + normal * random_vector.z).normal();
            new_normal = (random_vector.x, random_vector.y, random_vector.z)
            
            # ����ÿ������
            for vertex in vertices:
                cmds.polyNormalPerVertex(vertex, xyz=new_normal)

def show_window():
    window = cmds.window("RandomNormal", title="Random Normal Tool", widthHeight=(300, 200))
    cmds.columnLayout(adj = True, cal='right')
    cmds.floatSliderGrp(label = "MaxDistance",field=True,min=0.01,max=100,value=10,dc=print_face_vertices)
    cmds.button(label="Random",command=print_face_vertices)
    cmds.showWindow()
# ���ú���
show_window()

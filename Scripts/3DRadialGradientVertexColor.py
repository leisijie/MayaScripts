import maya.cmds as cmds
from math import pow,sqrt,sin

class VC_Window(object):
    def __init__(self):
        self.window = "VC_Window"
        self.title = "VertexColorGenerator"
        self.size = (400,400)
        
        if cmds.window(self.window,exists=True):
            cmds.deleteUI(self.window,window=True)
            
        self.window = cmds.window(self.window, title=self.title,widthHeight=self.size)
        
        cmds.columnLayout(adj = True)
        self.originObjText = cmds.textFieldGrp(label="Origin",text = "Please",ed=False)
        cmds.button(label="Set",command=lambda *_:self.SetOrigin())
        self.targetObjsText = cmds.textFieldGrp(label="Targets",text = "Please",ed=False)
        cmds.button(label="Set",command=lambda *_:self.SetTargets())
        self.maxDistance = cmds.floatSliderGrp(label = "MaxDistance",field=True,min=0.01,max=100,value=10)
        self.rgbExpression = cmds.textFieldGrp(label="RGB Expression(percent)",text = "pow(1-percent,10)")
        cmds.button(label="Start",command=lambda*_:self.RadialGradient())
        cmds.showWindow()
        
    def SetOrigin(self):
        self.originObj = cmds.ls(sl=True)[0]
        cmds.textFieldGrp(self.originObjText,text=self.originObj,e=True)
    
    def SetTargets(self):
        self.targetObjs = cmds.ls(sl=True)
        tx = ""
        for obj in self.targetObjs:
            tx += obj+"|"
        cmds.textFieldGrp(self.targetObjsText,text=tx,e=True)
    
    def RadialGradient(self):
        maxDistance = cmds.floatSliderGrp(self.maxDistance,q=True,v=True)
        
        originalPos = cmds.getAttr(self.originObj+".translate")[0]
        
        for obj in self.targetObjs:
            cmds.select(obj)
            vertexCount = cmds.polyEvaluate(v=True)
            print(vertexCount)
            for vtx in range(vertexCount):
                cmds.select(obj+".vtx"+"["+str(vtx)+"]")
                vtxPos = cmds.xform(q=True,ws=True,t=True)
                dis = sqrt(pow(vtxPos[0]-originalPos[0],2)+pow(vtxPos[1]-originalPos[1],2)+pow(vtxPos[2]-originalPos[2],2))
                percent = dis/maxDistance
                if percent > 1:
                    percent = 1
                expression = cmds.textFieldGrp(self.rgbExpression,q=True,tx=True)
                r = eval(expression)
                cmds.polyColorPerVertex(rgb=(r,r,r))
                #cmds.polyColorPerVertex(a=sin(percent*10))
                
    def LinearGradient(self):
        endPosition = (0,0,)
        originalPos = cmds.getAttr(self.originObj+".translate")[0]
        
        for obj in self.targetObjs:
            cmds.select(obj)
            vertexCount = cmds.polyEvaluate(v=True)
            for vtx in range(vertexCount):
                cmds.select(obj+".vtx"+"["+str(vtx)+"]")
                vtxPos = cmds.xform(q=True,ws=True,t=True)
                dis = sqrt(pow(vtxPos[0]-originalPos[0],2)+pow(vtxPos[1]-originalPos[1],2)+pow(vtxPos[2]-originalPos[2],2))
                percent = dis/maxDistance
                if percent > 1:
                    percent = 1
                expression = cmds.textFieldGrp(self.rgbExpression,q=True,tx=True)
                r = eval(expression)
                cmds.polyColorPerVertex(rgb=(r,r,r))
                #cmds.polyColorPerVertex(a=sin(percent*10))
        
        
vc_window = VC_Window()




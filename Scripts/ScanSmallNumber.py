import maya.cmds as cmds 

curves = cmds.ls(type="animCurve")
for cv in (cv for cv in curves if 'scale' in cv): #only scan scale curves
    keys = cmds.keyframe(cv,q=True)
    if keys != None:
        for key in keys:
            value = cmds.keyframe(cv,q=True,time=(key,key),eval=True)
            if(value[0]<0.01):
                object = cmds.listConnections(cv)#get connected objects
                cmds.keyframe(cv,e=True,time=(key,key),valueChange=0.01)
                try:
                    if len(object) > 0:
                        print(str(cv))
                        print(str(object) +' has a small value '+ str(value[0]) +' at '+str(key))
                except:
                    print(str(cv))
                        
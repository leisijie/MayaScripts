import maya.cmds as cmds

pluginName = 'RandomNormal'
nodeName = 'RandomNormalNode'
path = 'T:\work\MayaScripts\Plugin\RandomNormal.py'

cmds.flushUndo()
plugList = cmds.pluginInfo( query=True, listPlugins=True )
if(pluginName in plugList):
    plugNodeTypeList = cmds.pluginInfo(pluginName,query=True,dependNode=True)
    for plugNodeType in plugNodeTypeList :
        existingNodes = cmds.ls(type = plugNodeType)
        if(existingNodes):
            cmds.delete(existingNodes)
            print("Deleted nodes: %s"%existingNodes)
    cmds.flushUndo()
    removedPluginList = cmds.unloadPlugin(pluginName+'.py')
    print("Removed plugins£º%s"%removedPluginList)
    
cmds.loadPlugin( path )
cmds.createNode( nodeName )
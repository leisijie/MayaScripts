import maya.api.OpenMaya as OpenMaya
import random
import math

def maya_useNewAPI():
    pass
    
kPluginNodeName = 'RandomNormalNode'              # The name of the node.
kPluginNodeClassify = 'utility/general'     # Where this node will be found in the Maya UI.
kPluginNodeId = OpenMaya.MTypeId( 0x87EFF ) # A unique ID associated to this node type.

##########################################################
# Plug-in 
##########################################################
class randomNormalNode(OpenMaya.MPxNode):
    inMesh = OpenMaya.MObject()
    outMesh = OpenMaya.MObject()
    maxAngle = OpenMaya.MObject()
    seedNum = OpenMaya.MObject()
    
    def __init__(self):
        OpenMaya.MPxNode.__init__(self)
        
    def compute(self,pPlug,pDataBlock):
        if(pPlug==randomNormalNode.outMesh):
            inputMeshHandle = pDataBlock.inputValue(randomNormalNode.inMesh)
            inputMeshValue = inputMeshHandle.asMesh()
            
            maxAngleHandle = pDataBlock.inputValue(randomNormalNode.maxAngle)
            maxAngleValue = maxAngleHandle.asFloat()
            
            seedHandle = pDataBlock.inputValue(randomNormalNode.seedNum)
            seedValue = seedHandle.asInt()
            
            outputMeshHandle = pDataBlock.outputValue(randomNormalNode.outMesh)
            outputMeshValue = outputMeshHandle.asMesh()
            
            random.seed(seedValue)
            randomNormalCompute(inputMeshValue,maxAngleValue/180)
            
            outputMeshHandle.setMObject(inputMeshValue)
            outputMeshHandle.setClean()
        else:
            return OpenMaya.kUnknownParameter

##########################################################
# Plug-in initialization.
##########################################################
def nodeCreator():
    ''' Creates an instance of our node class and delivers it to Maya as a pointer. '''
    return  randomNormalNode()

def nodeInitializer():
    floatAttributeFn = OpenMaya.MFnNumericAttribute()
    typedAttributeFn = OpenMaya.MFnTypedAttribute()
    #Input Attribute
    randomNormalNode.inMesh = typedAttributeFn.create('InMesh','InMesh',OpenMaya.MFnData.kMesh)
    typedAttributeFn.writable = True
    typedAttributeFn.readable = True
    typedAttributeFn.connectable = True
    randomNormalNode.addAttribute(randomNormalNode.inMesh)
    
    randomNormalNode.maxAngle = floatAttributeFn.create('maxAngle','maxAngle',OpenMaya.MFnNumericData.kFloat,30)
    floatAttributeFn.writable = True
    floatAttributeFn.readable = True
    floatAttributeFn.storable = False
    floatAttributeFn.setMin(0)
    floatAttributeFn.setMax(180)
    randomNormalNode.addAttribute(randomNormalNode.maxAngle)
    
    randomNormalNode.seedNum = floatAttributeFn.create('Seed','Seed',OpenMaya.MFnNumericData.kInt,30)
    floatAttributeFn.writable = True
    floatAttributeFn.readable = True
    floatAttributeFn.storable = False
    randomNormalNode.addAttribute(randomNormalNode.seedNum)
    
    #Output Attribute
    randomNormalNode.outMesh = typedAttributeFn.create('OutMesh','OutMesh',OpenMaya.MFnData.kMesh)
    typedAttributeFn.writable = True
    typedAttributeFn.readable = True
    typedAttributeFn.connectable = True
    randomNormalNode.addAttribute(randomNormalNode.outMesh)
    #Affect
    randomNormalNode.attributeAffects(randomNormalNode.inMesh,randomNormalNode.outMesh)
    randomNormalNode.attributeAffects(randomNormalNode.maxAngle,randomNormalNode.outMesh)
    randomNormalNode.attributeAffects(randomNormalNode.seedNum,randomNormalNode.outMesh)
    
def initializePlugin( mobject ):
    ''' Initialize the plug-in '''
    mplugin = OpenMaya.MFnPlugin( mobject )
    try:
        mplugin.registerNode( kPluginNodeName, kPluginNodeId, nodeCreator,
                              nodeInitializer, OpenMaya.MPxNode.kDependNode, kPluginNodeClassify )
    except:
        sys.stderr.write( 'Failed to register node: ' + kPluginNodeName )
        raise

def uninitializePlugin( mobject ):
    ''' Uninitializes the plug-in '''
    mplugin = OpenMaya.MFnPlugin( mobject )
    try:
        mplugin.deregisterNode( kPluginNodeId )
    except:
        sys.stderr.write( 'Failed to deregister node: ' + kPluginNodeName )
        raise

############################################
#Random Normal Compute
############################################

def randomNormalCompute(inMeshValue : OpenMaya.MObject, maxAngle : float):
    mesh_fn = OpenMaya.MFnMesh(inMeshValue)
    face_iter = OpenMaya.MItMeshPolygon(inMeshValue)
    
    tangents = mesh_fn.getTangents()
    while not face_iter.isDone():
        vertex_ids = face_iter.getVertices()
        face_id = face_iter.index()
        face_ids = [face_id] * len(vertex_ids)

        #Get normal-tangent-binormal
        normal_old = face_iter.getNormal()

        tangent = OpenMaya.MVector(face_iter.point(0)) - OpenMaya.MVector(face_iter.point(1))
        tangent = tangent.normal()

        binormal = (normal_old ^ tangent).normal()

        #compute new Normal
        phi = random.random() * math.pi * maxAngle
        theta = random.random() * math.pi * 2
        # random vector
        random_vector = OpenMaya.MVector(math.cos(theta) * math.sin(phi), math.sin(theta) * math.sin(phi), math.cos(phi)).normal()
        normal_new = (binormal  * random_vector.x + tangent * random_vector.y + normal_old * random_vector.z).normal();
        normal_news = [normal_new] * len(vertex_ids)
        #set new Normal
        mesh_fn.setFaceVertexNormals(normal_news,face_ids,vertex_ids)

        face_iter.next()
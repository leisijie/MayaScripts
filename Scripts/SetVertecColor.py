import maya.cmds as cmds

class VertexColorTool:
    def __init__(self):
        self.create_vertex_color_window()

    def set_vertex_color(self, value):
        selection = cmds.ls(selection=True, flatten=True)
        if not selection:
            cmds.warning("Please select at least one vertex.")
            return
        for vertex in selection:
            c = value / 256
            cmds.polyColorPerVertex(vertex, colorRGB=(c, c, c))

    def update_shell_list(self, *args):
        selection = cmds.ls(selection=True, flatten=True)
        if not selection:
            cmds.warning("Please select at least one object.")
            return
        cmds.textScrollList(self.shellList, edit=True, removeAll=True)  # Çå¿ÕÁÐ±í
        obj = selection[0]
        if obj:
            max_vertex_count = cmds.polyEvaluate(obj,v=True)
            
            verteices_list = list(range(max_vertex_count)) 
            
            start_index = 0
            end_index = -1
            shell_vertex_count = 0
            counted_vertices = 0
            while(counted_vertices<max_vertex_count):
                cmds.select( clear=True )
                start_index = end_index + 1
                
                cmds.select(obj+'.vtx[{}]'.format(start_index),replace=True)
                cmds.polySelectConstraint(mode=2,shell = True)
                cmds.polySelectConstraint(disable = True)
                selected_vertices = cmds.ls(selection=True, flatten=True)
                print(selected_vertices)
                shell_vertex_count = len(selected_vertices)
                
                
                end_index = start_index + shell_vertex_count - 1
                counted_vertices += shell_vertex_count
                
                value = "{}.vtx[{}:{}]".format(obj,start_index,end_index)
                cmds.textScrollList(self.shellList, edit=True, append= value)

    def select_vertices_from_list(self, *args):
        selected_items = cmds.textScrollList(self.shellList, query=True, selectItem=True)
        if selected_items:
            cmds.select(clear=True)
            for item in selected_items:
                cmds.select(item, add=True)

    def create_vertex_color_window(self):
        values = [0, 2, 4, 8, 16, 32, 64, 128, 256]
        if cmds.window("vertexColorWindow", exists=True):
            cmds.deleteUI("vertexColorWindow", window=True)

        window = cmds.window("vertexColorWindow", title="Vertex Color Tool", widthHeight=(300, 200))
        cmds.columnLayout(adjustableColumn=True)
        cmds.separator(style="none", height=10)
        cmds.text(label="Set Vertex Value:")
        cmds.gridLayout(numberOfColumns=2, cellWidthHeight=(100, 30))
        for value in values:
            cmds.button(label=str(value), command=lambda x, y=value: self.set_vertex_color(y))
        cmds.setParent("..")

        cmds.separator(style="none", height=10)
        cmds.button(label="Update Shell List", command=self.update_shell_list)
        self.shellList = cmds.textScrollList(numberOfRows=10, allowMultiSelection=False, selectCommand=self.select_vertices_from_list)
        
        cmds.showWindow(window)

VertexColorTool()

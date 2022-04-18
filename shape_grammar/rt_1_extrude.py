import bpy
import bmesh
import mathutils
import math
from mathutils import Vector
import random
from random import randrange



import  os, sys, importlib

 
'''
CollectionRoutines.py needs to be stored in a folder called lib
in the same directory as this file. 
this loads the CollectionRoutines.py file
'''

dir = os.path.dirname(bpy.data.filepath)+"\lib"
sys.path.append(dir)
import CollectionRoutines
# must be run twice to pick up changes from edits to alpha.py
importlib.reload(CollectionRoutines)
'''  ---------------------------------------- '''




'''
ExtrudeFacesIndividualAlongNormal
params:
    bm: BMesh to operate on
    face_list: list of faces to extrude
    extrude_amount: amount of extrusion


'''
def ExtrudeFacesIndividualAlongNormal(bm, face_list, extrudeAmount):
    extrudedFaces = bmesh.ops.extrude_discrete_faces(bm, faces = face_list)
    for face in extrudedFaces["faces"]:        
        normal = face.normal
        for vert in face.verts:
            vert.co += extrudeAmount * normal
 



'''
createBaseCube
params: none

returns the object reference to the created object

'''
def createBaseCube( ):
    #create cube
    bpy.ops.mesh.primitive_cube_add(enter_editmode=False)
    obj = bpy.context.selected_objects[0]
    me = obj.data
     
    loc = Vector([-1,-1,-1])
     
    #create bmesh from cube
    bm = bmesh.new()   
    bm.from_mesh(me)                               
     
    # move origin to corner
    bmesh.ops.translate(bm,
       verts = bm.verts,
       vec = -loc,
       )
    #compute the face access indices for the first extrude   
    bm.faces.ensure_lookup_table() 
    firstboxSize = len(bm.faces)
    a1 = randrange(0,firstboxSize)
    a2 = randrange(0,firstboxSize)
    
    while a2 == a1:
        a2 = randrange(0,firstboxSize)
    
    
    firstLength = randrange(1,6)
    secondLength = randrange(1,6)


    face_list = [bm.faces[a1],bm.faces[a2]]
    ExtrudeFacesIndividualAlongNormal(bm,face_list,firstLength)
    
    
    #compute the face access indices for the second extrude       
    bm.faces.ensure_lookup_table() 
    secondboxSize = len(bm.faces)
    b1 = randrange(0,secondboxSize)
    b2 = randrange(0,secondboxSize)
    
    while b2 == b1:
        b2 = randrange(0,secondboxSize)
        
    b3 = randrange(0,secondboxSize)
    
    while b3 == b1 or b3 == b2:
        b3 = randrange(0,secondboxSize)

    
    
    face_list = [bm.faces[b1],bm.faces[b2],bm.faces[b3]]
    ExtrudeFacesIndividualAlongNormal(bm,face_list,secondLength)    
       
    #commit the bmesh back into the object   
    me = bpy.context.object.data    #object
    bm.to_mesh(me) #bind the bmesh to the object
    bm.free()   
       
       
    return obj
'''
moveObject
params:
    idx: the index for a given group of objects
    offset:  grouping value

'''
def moveObject(idx,offset):
    
    
    ee = "idx {0:1}, offset {1:1}, x {2:1}, y {3:1}, z {4:1}"
   
    rowSize = 4
    mainLocation = 50
    rowspacing = 25
    me = bpy.context.object    
    rm = idx % rowSize  
    zval = math.floor(idx/rowSize)
    z =  zval*rowspacing
    x = mainLocation+ rm* rowspacing
    
    y = offset * rowspacing
    #print(ee.format(idx,offset,x,y,z))
    me.matrix_world.translation = Vector([x,y,z])
  
    
  #S  loc = Vector([x,y,z])
    
#    bmesh.ops.translate(bm,
#       verts = bm.verts,
#       vec = -loc,
#       )

'''
rotate
params:
    ang: angle to rotate an object in degrees
 
'''
def rotate(ang):
    r = ((2*3.14)/360) *ang
    bpy.ops.transform.rotate(value=r, orient_axis='Z')
 

###################### stackable ###############################################       

def rotate0():
    return rotate(0)
    
def rotate45():
    return rotate(45)

def rotate90():
    return rotate(90)

def rotate135():
    return rotate(135)

def rotate180():
    return rotate(180)

def mirrorY():
    bpy.ops.transform.mirror(constraint_axis=(False, True, False))

def mirrorX():
    bpy.ops.transform.mirror(constraint_axis=(True,False, False))
#################################################################################

'''
createMainActionList
params: none

creates mainAction which is a list of lists. Each list is a collection
of rotations and mirrors function calls

example element in mainAction: [rotate45,mirrorX], [rotate45,mirrorY]....

'''
def createMainActionList():
    mainAction = []
    rotList = [rotate0,rotate45,rotate90,rotate135,rotate180]
    mirrorList = [mirrorX,mirrorY]
    rotRange = range (0,len(rotList))
    mirrorRange = range(0,len(mirrorList))
    
    for i in rotRange:
        tempList = []
        tempList.append(rotList[i])
        mainAction.append(tempList)
        
        for j in mirrorRange:
            triList = tempList.copy()
            triList.append(mirrorList[j])
            mainAction.append(triList)
          
   

    return mainAction

'''
https://blenderartists.org/t/how-to-apply-all-the-modifiers-with-python/1314483

most operators use a classmethod called poll that determines whether or
not the operator is allowed to run. if this check fails, you will get
the ‘context incorrect’ error. the API understands that you will sometimes
need to fire an operator from some arbitrary context, so it allows you to pass
in an overridden context (which is what I’ve done in my example 
with ctx = bpy.context.copy(). Once you’ve got an overridden context you can
set the keys to whatever values the operator is expecting. This is actually
the trickiest part, because there’s no way to know what an operator’s poll()
is looking for without opening up the source code and checking. Once you’ve done
 it a few times you get a feel for what operators are looking for via trial and error.

What you were attempting to do in your code is create the context by manually
selecting the object as the user might do- the problem is that when you select 
an object in this manner it is not active, and most operators are going to require 
an active object. So if you wanted to, you could also fix your original code that way, 
but the ‘more correct’ way to do it is via context overrides (since it doesn’t change 
the user’s selection or anything like that).

'''
def apply_modifiers(obj):
    ctx = bpy.context.copy()
    ctx['object'] = obj
    for _, m in enumerate(obj.modifiers):
        try:
            ctx['modifier'] = m
            bpy.ops.object.modifier_apply(ctx, modifier=m.name)
        except RuntimeError:
            print(f"Error applying {m.name} to {obj.name}, removing it instead.")
            obj.modifiers.remove(m)

    for m in obj.modifiers:
        obj.modifiers.remove(m)



 
def main():
    
    #center cursor
    bpy.context.scene.cursor.location = (0,0,0) 
    layerName = "pieces"
    #create collection
    actionList =  createMainActionList()
    CollectionRoutines.addLayerCollection(layerName)
    piecesLayer= CollectionRoutines.selectLayer(layerName) 
    iters = range(0,3) #number of objects
    idx = 0
    originals = []
    for k in iters:
        oo = createBaseCube()
       #save the name of the originals
        originals.append(oo.name)
        
        # for each stack of rotations, mirrors
        for j in range(0,len(actionList)):
            
            # when copying send to origin as a copy is at the position 
            # of the last object and thus its world matrix will accumulate
            #duplicate the object
            bpy.ops.object.duplicate_move(TRANSFORM_OT_translate={"value":(0,0,0)})
            # make a copy of the selected current obj, which is oo
            # it is now selected
            me = bpy.context.object.data
            #create a new bmesh
            bm = bmesh.new()   
            bm.from_mesh(me)
            functionList = actionList[j]
            #for each action (rotation,mirror) in the sub lists
            funcIter = range(0,len(functionList))
            for a in funcIter: 
                functionList[a]()
            bpy.ops.object.mode_set( mode = 'OBJECT' ) 
            moveObject(j,k)
            #commit the mesh
            bm.to_mesh(me)
            bm.free()  
            #commit transforms
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

           
     #   delete the original objects by name
     #   stored by name in array originals
    
    objs = bpy.data.objects
    for z in originals:
       objs.remove(objs[z], do_unlink=True)
#########################################################



    bpy.ops.object.select_all(action='TOGGLE')
    cubes = piecesLayer.collection.all_objects
    
    for obj in cubes:
 
        # Add the modifier the low level function and set the bevel amount
        bevel_mod = obj.modifiers.new(name="MY-Bevel"+obj.name, type='BEVEL')
        bevel_mod.width = 0.05        
        #print(obj.name)
        
    for obj in cubes:
        apply_modifiers(obj)
        

main()  

  
  
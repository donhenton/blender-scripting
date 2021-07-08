import bpy
import bmesh
import numpy as np
from mathutils import Vector, Matrix
from math import sqrt
import itertools
import utils
from math import pi

def tetrahedronPoints(r=1, origin=(0, 0, 0)):
    origin = Vector(origin)

    # Formulas from http://mathworld.wolfram.com/RegularTetrahedron.html
    a = 4*r/sqrt(6)
    h = a*sqrt(6)/3
    points = [( sqrt(3)*a/3,  0, -r/3), \
              (-sqrt(3)*a/6, -0.5*a, -r/3), \
              (-sqrt(3)*a/6,  0.5*a, -r/3), \
              (0, 0, sqrt(6)*a/3 - r/3)]

    points = [Vector(p) + origin for p in points]
    return points


def recursiveTetrahedron(bm, points, level=0):
    subTetras = []
    for i in range(len(points)):
        p0 = points[i]
        pK = points[:i] + points[i + 1:]
        subTetras.append([p0] + [(p0 + p)/2 for p in pK])

    if 0 < level:
        for subTetra in subTetras:
            recursiveTetrahedron(bm, subTetra, level-1)
    else:
        for subTetra in subTetras:
            verts = [bm.verts.new(p) for p in subTetra]
            faces = [bm.faces.new(face) for face in itertools.combinations(verts, 3)]
            bmesh.ops.recalc_face_normals(bm, faces=faces)


if __name__ == '__main__':
    # Remove all elements
    utils.removeAll()


    # Creata fractal tetrahedron
    bm = bmesh.new()
    tetrahedronBasePoints = tetrahedronPoints(5)
    recursiveTetrahedron(bm, tetrahedronBasePoints, level=4)

    # Create obj and mesh from bmesh object
    me = bpy.data.meshes.new("TetrahedronMesh")
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new("Tetrahedron", me)
    #bpy.context.scene.objects.link(obj)
    bpy.context.collection.objects.link(obj)
    #bpy.context.scene.update()
    bpy.context.view_layer.update()

    # Create camera and lamp
    target = utils.target((0, 0, 1))
    cameraObj = utils.camera((-8, 10, 5), target, type='ORTHO', ortho_scale=16)
   # utils.lamp((10, -10, 10),5, target=target, type='SUN')
    
    utils.lamp((10, -10, 10),energy=15,color=(1,0.93,0.5),target=target, type='SUN')
    utils.lamp((10, 10, 10),energy=5,color=(0.241,0.358,0.9),target=target, type='SUN')
#   

    # Enable ambient occlusion
    utils.setAmbientOcclusion(samples=10)

    # Select colors
    palette = [(50,80,70,255), (218,122,61,255)]
    palette = [utils.colorRGB_256(color) for color in palette]  # Adjust color to Blender

    # Set background color of scene
    # bpy.context.scene.world.horizon_color = palette[0]
    # bpy.data.worlds["World"].color =(0,0,0)
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = palette[0]

    # Set material for object
    
    
    mat = utils.simpleMaterial(palette[1])
    obj.data.materials.append(mat)

    # Render scene
    
     # Make target as parent of camera
    cameraObj.parent = target

    # Set number of frames
    bpy.context.scene.frame_end = 200
    
        # Animate rotation of target by keyframe animation
    target.rotation_mode = 'AXIS_ANGLE'
    target.rotation_axis_angle = (0, 0, 0, 1)
    target.keyframe_insert(data_path='rotation_axis_angle', index=-1,
        frame=bpy.context.scene.frame_start)
    target.rotation_axis_angle = (2*pi, 0, 0, 1)
    # Set last frame to one frame further to have an animation loop
    target.keyframe_insert(data_path='rotation_axis_angle', index=-1,
        frame=bpy.context.scene.frame_end + 1)

    # Change each created keyframe point to linear interpolation
    for fcurve in target.animation_data.action.fcurves:
        for keyframe in fcurve.keyframe_points:
            keyframe.interpolation = 'LINEAR'
    
    
    
    
    
    utils.renderToFolder('tetra_render', 'tetrahedron_fractal', 1920, 1080, animation=True)
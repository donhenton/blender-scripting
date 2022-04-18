# This example assumes we have a mesh object selected

import bpy
import bmesh

## This first part works like a charm, and it prints out the vertices perfectly.
obj = bpy.context.active_object
v = obj.data.vertices[1]
#coords = [(obj.matrix_world * v.co) for v in obj.data.vertices]
print(v.co)
print(obj.matrix_world)
print(len(obj.data.vertices))

#plain_coords = [vert.to_tuple() for vert in coords]
#print(plain_coords)

## This is the part I need help on. No matter what I try it keeps saying there is no attribute 
#f = obj.faces
#print(f)
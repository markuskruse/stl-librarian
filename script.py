import os, bpy, sys, glob, math

from math import radians
from PIL import Image, ImageDraw

########################################
#
# Mandatory parameters
# set these paths and then click run script
# examples for windows, linux and mac can be found below
#
########################################

#source_dir = "/home/user/librarian"
#target_dir = "/home/user/librarian"
source_dir = "C:/tmp/register/"
target_dir = "C:/tmp/register/"

########################################
#
# Parameters with sensible defaults
#
########################################

width = 500
height = 500
anim_frames = 16
anim_seconds = 3
anim_scale = 50

########################################
#
# program start
#
########################################

#render settings
scene = bpy.data.scenes["Scene"]
scene.render.resolution_x = width
scene.render.resolution_y = height
scene.render.image_settings.file_format='JPEG'

#this script two materials to be present in the scene
mat = bpy.data.materials.get("Material") #used for the object itself
textmat = bpy.data.materials.get("TextMaterial") #used for the label

pi = 3.14159265

cam_rot = scene.camera.rotation_euler

bpy.ops.object.select_all(action='DESELECT')

#new empty list to save image names in for later creating html-view
images = []

files = glob.glob(os.path.join(source_dir, "*%s" % "stl"))
files.sort()

for i, fp in enumerate(files):
    if (i < 1000): #set this to a low value for testing
        #load model
        bpy.ops.import_mesh.stl(filepath=fp)
        ob = bpy.context.active_object
        modelname = ob.name

        #get center of object
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')
        ob.location = (0, 0, 0)
                        
        #set material
        ob.data.materials.append(mat)

        #calculate good text position
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        x = ob.location.x
        y = ob.location.y
        z = ob.location.z + max(ob.dimensions.z / 1.2, ob.dimensions.x / 2, ob.dimensions.y / 2)

        #create label
        bpy.ops.object.text_add(location=(x,y,z), radius=1)
        textobject=bpy.context.object
        textobject.data.body = modelname
        
        #position text
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        textobject.location = (x, y, z)

        #align text to camera
        textobject.rotation_euler = cam_rot
        
        #scale text to match model
        obj_size = math.sqrt(ob.dimensions[0]**2 + ob.dimensions[1]**2 + ob.dimensions[2]**2)
        text_size = math.sqrt(textobject.dimensions[0]**2 + textobject.dimensions[1]**2 + textobject.dimensions[2]**2)
        scale = obj_size / (text_size * 2)
        textobject.scale = (scale, scale, scale)

        #text material
        textobject.data.materials.append(textmat)

        #focus camera on object
        ob.select_set(True)
        textobject.select_set(True)
        scene.camera.data.angle = radians(45)
        bpy.ops.view3d.camera_to_view_selected()
        scene.camera.data.angle = radians(50)
        
        #set render properties and render
        scene.render.resolution_percentage = 100
        bpy.context.scene.render.filepath = target_dir + modelname + ".jpg"
        bpy.ops.render.render(use_viewport = True, write_still=True)
        images.append(modelname)

        #Delete text
        ob.select_set(False)
        bpy.ops.object.delete() 
        ob.select_set(True)
        
        #reposition camera
        scene.camera.data.angle = radians(45)
        bpy.ops.view3d.camera_to_view_selected()
        scene.camera.data.angle = radians(50)
        loc = scene.camera.location
        camera_z = scene.camera.location[2]
        distance = math.sqrt(loc[0] * loc[0] + loc[1] * loc[1])

        animnames = []
        for index in range(anim_frames):
            # rotate camera based on angle
            angle = index * (360 / anim_frames)
            scene.camera.rotation_euler = (radians(45), 0.0, radians(angle))
            scene.camera.location = (math.sin(radians(angle)) * distance, -1 * math.cos(radians(angle)) * distance, camera_z)
            
            #set render properties and render
            scene.render.resolution_percentage = anim_scale
            filename = target_dir + "frame_" + str(index) + ".jpg"
            animnames.append(filename)
            bpy.context.scene.render.filepath = filename
            bpy.ops.render.render(use_viewport = True, write_still=True)

        anim = []
        for index in range(anim_frames):
            im = Image.open(animnames[index])
            anim.append(im)
            
        gifim = anim[0]
        gifim.save(target_dir + modelname + "_anim.gif", save_all=True, optimize=True, append_images=anim[1:anim_frames], duration=anim_seconds/anim_frames, loop=0)

        #delete object
        bpy.ops.object.delete() 

html_top = """
<!doctype html>

<html>
    <head>
        <style>"""

css_template= """
        div.img{0} {{
            background-image: url('{1}.jpg');
            width: {2}px;
            height: {3}px;
            display: inline-block;
            border: 1px solid black;
        }}
        div.img{0}:hover {{
            background-image: url('{1}_anim.gif');
            background-size: contain;
        }}"""

image_template = """
<div class="img{0}" title="{1}">&nbsp;</div>"""

with open(target_dir + "stl-model-register.html", "w") as file:
    file.write(html_top)
    for i, image in enumerate(images):
        file.write(css_template.format(i, image, width, height))
    file.write("</style></head><body>")
    for i, image in enumerate(images):
        file.write(image_template.format(i, image))
    file.write("</body></html>")
    
for index in range(anim_frames):
    os.remove(animnames[index])

print("Ook")

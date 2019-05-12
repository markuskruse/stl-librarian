import os, bpy, sys, glob, math

########################################
#
# set these paths and then click run script
#
########################################
source_dir = "C:/path-to/your/dir"
target_dir = "C:/tmp/"

#render settings
scene = bpy.data.scenes["Scene"]
scene.render.resolution_x = 500
scene.render.resolution_y = 500
scene.render.resolution_percentage = 100
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
        
        #set material
        ob.data.materials.append(mat)

        #calculate good text position
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        x = ob.location.x
        y = ob.location.y
        z = ob.location.z + ob.dimensions.z / 1.5

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
        print (obj_size)
        text_size = math.sqrt(textobject.dimensions[0]**2 + textobject.dimensions[1]**2 + textobject.dimensions[2]**2)
        print (text_size)
        scale = obj_size / (text_size * 2)
        print ("scale", scale)
        textobject.scale = (scale, scale, scale)

        #text material
        textobject.data.materials.append(textmat)

        #focus camera on object
        ob.select_set(True)
        textobject.select_set(True)
        scene.camera.data.angle = 45*(pi/180.0)
        bpy.ops.view3d.camera_to_view_selected()
        scene.camera.data.angle = 50*(pi/180.0)
        
        #set render properties and render
        bpy.context.scene.render.filepath = target_dir + modelname + ".jpg"
        bpy.ops.render.render(use_viewport = True, write_still=True)
        print("STL rendered: ", ob.name)
        images.append(modelname + ".jpg")

        #delete object
        bpy.ops.object.delete() 

with open(target_dir + "stl-model-register.html", "w") as file:
    file.write("<html><body>")
    for i, image in enumerate(images):
        print("Image: ", image)
        file.write("<img src=\"%s\" alt=\"%s\">\n" % (image, image))
    file.write("</body></html>")
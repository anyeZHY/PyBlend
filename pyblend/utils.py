import os
import bpy


def clear():
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj)
    for m in bpy.data.meshes:
        bpy.data.meshes.remove(m)
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat)
    for img in bpy.data.images:
        bpy.data.images.remove(img)


class BlenderRemover:
    def __init__(self):
        self.mats = []
        self.objs = []
        self.meshes = []
        self.imgs = []

    def add(self, obj: bpy.types.Object = None, img: bpy.types.Image = None):
        if obj is not None:
            self.objs.append(obj)
            self.mats.append(obj.active_material)
            self.meshes.append(obj.data)
        if img is not None:
            self.imgs.append(img)

    def __call__(self):
        for mat in self.mats:
            if mat is not None:
                bpy.data.materials.remove(mat)
        for obj in self.objs:
            bpy.data.objects.remove(obj)
        for mesh in self.meshes:
            bpy.data.meshes.remove(mesh)
        for img_name in self.imgs:
            if bpy.data.images.get(img_name) is not None:
                bpy.data.images.remove(bpy.data.images[img_name])


def debug(file_path="debug.blend"):
    """Save the current scene to a blend file for debugging

    Args:
        file_path (str, optional): path to save the blend file. Defaults to "debug.blend".
    """
    print(f"Saving debug file to {os.path.abspath(file_path)}")
    bpy.ops.wm.save_as_mainfile(filepath=file_path)

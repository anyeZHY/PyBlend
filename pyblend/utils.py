import os
import bpy
import sys
import argparse
from typing import List


class ArgumentParserForBlender(argparse.ArgumentParser):
    """
    Reference: https://blender.stackexchange.com/a/134596
    This class is identical to its superclass, except for the parse_args
    method (see docstring). It resolves the ambiguity generated when calling
    Blender from the CLI with a python script, and both Blender and the script
    have arguments. E.g., the following call will make Blender crash because
    it will try to process the script's -a and -b flags:
    >>> blender --python my_script.py -a 1 -b 2

    To bypass this issue this class uses the fact that Blender will ignore all
    arguments given after a double-dash ('--'). The approach is that all
    arguments before '--' go to Blender, arguments after go to the script.
    The following calls work fine:
    >>> blender --python my_script.py -- -a 1 -b 2
    >>> blender --python my_script.py --
    """

    def _get_argv_after_doubledash(self, args=None):
        """
        Given the sys.argv as a list of strings, this method returns the
        sublist right after the '--' element (if present, otherwise returns
        an empty list).
        """
        if args is not None:
            return args
        try:
            idx = sys.argv.index("--")
            return sys.argv[idx + 1 :]  # the list after '--'
        except ValueError as e:  # '--' not in the list:
            return []

    def parse_known_args(self, args=None, namespace=None):
        """
        This method is expected to behave identically as in the superclass,
        except that the sys.argv list will be pre-processed using
        _get_argv_after_doubledash before. See the docstring of the class for
        usage examples and details.
        """
        return super().parse_known_args(args=self._get_argv_after_doubledash(args), namespace=None)


class BlenderRemover:
    """
    This class is used to remove objects, meshes, materials, and images
    created by Blender. It is used to remove temporary objects created
    during the rendering process.

    To remove objects, meshes, materials, and images, simply call
    >>> remover = BlenderRemover()  # create a remover
    >>> remover.add(obj, img)  # add objects to be removed
    >>> remover()  # remove objects

    If you want to remove all objects, meshes, materials, and images
    created by Blender, simply call
    >>> remover.clear_all()
    """

    def __init__(self):
        self.mats = []
        self.objs = []
        self.meshes = []
        self.imgs = []

    def add(self, obj: bpy.types.Object = None, img: bpy.types.Image = None):
        if obj is not None:
            self.objs.append(obj)
            if obj.active_material is not None:
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

        self.reset()

    def reset(self):
        self.mats = []
        self.objs = []
        self.meshes = []
        self.imgs = []

    def clear_all(self, exclude=[]):
        """
        Clear all objects, meshes, materials, and images created by Blender

        Args:
            exclude (List): objects, meshes, materials, and images to be excluded
        """
        for mat in bpy.data.materials:
            if mat not in exclude or mat.name not in exclude:
                bpy.data.materials.remove(mat)
        for obj in bpy.data.objects:
            # keep camera if only one camera is left
            if obj.type == "CAMERA" and len(bpy.data.cameras) == 1:
                continue
            if obj not in exclude or obj.name not in exclude:
                bpy.data.objects.remove(obj)
        for mesh in bpy.data.meshes:
            if mesh not in exclude or mesh.name not in exclude:
                bpy.data.meshes.remove(mesh)
        for img in bpy.data.images:
            if (img not in exclude or img.name not in exclude) and img.users == 0:
                bpy.data.images.remove(img)


def debug(file_path="debug.blend"):
    """
    Save the current scene to a blend file for debugging

    Args:
        file_path (str, optional): path to save the blend file. Defaults to "debug.blend".
    """
    print(f"Saving debug file to {os.path.abspath(file_path)}")
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(file_path))

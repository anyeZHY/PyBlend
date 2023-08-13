<h1 align="center"> PyBlend </h1>

<p align="center">
    <b>PyBlend is a Python library for <a href="https://www.blender.org/">Blender</a>. It provides a lot of valuable functions for Blender scripting.</b>
</p>
<p align="center">
    <img src="docs/teaser.gif" width=80%>
    <p align="center">
        <b>Figure 1.</b> <i>Depth maps, random material images, and normal maps rendered using PyBlend with the Stanford Bunny.</i>
    </p>
</p>

## Installation

Setting up the environment for Python in Blender is a challenge. However, following the steps below, you can easily configure the environment.

1. Download Blender from [here](https://www.blender.org/download/).
    
    Note: if your project has strict environmental requirements, you must carefully select the version of Blender. Currently, there appears to be **NO** official release of Blender that directly supports Python 3.8, which can be verified from [blender/tags](https://github.com/blender/blender/tags). Here I use `blender-3.3.1-linux-x64.tar.xz` for Linux users with Python 3.10.2.
    Once you unzip the file, you will find a folder structured like this:

    ```bash
    ./blender-3.3.1-linux-x64
    ├── blender
    ├── 3.3
    ...
    ```
    where `blender` is the executable file (I will use `{path/to/blender}` or `blender_app` to represent this path in the following) and `3.3` contains the Python environment for Blender.

2. Download `get-pip.py` and install pip for Blender Python.

    ```bash
    $ wget https://bootstrap.pypa.io/get-pip.py

    $ ./blender-3.3.1-linux-x64/3.3/python/bin/python3.10 get-pip.py
    ```

3. Install PyBlend.

    ```bash
    $ ./blender-3.3.1-linux-x64/3.3/python/bin/pip install git+https://github.com/anyeZHY/PyBlend.git
    ```

4. You could install other packages in the same way. E.g.,

    ```bash
    $ ./blender-3.3.1-linux-x64/3.3/python/bin/pip install torch
    ```


## Usage
Some functions of this package are used in [3D-LLM: Injecting the 3D World into Large Language Models](https://vis-www.cs.umass.edu/3dllm/) and [CHORD: Category-level in-Hand Object Reconstruction via Shape Deformation]() [ICCV 2023].

I suggest using the following alias to simplify the command: `alias blender_app='{path/to/blender}'`.

### 1. Render Normal and Depth Images

Like teaser.gif, you can use PyBlend to render normal and depth images. By using the following command, you can generate 60 images ranging from 0 to 60 degrees.

```shell
$ blender_app -b -P scripts/teaser.py -- --begin 0 --end 60
```

### 2. OBJ in, Multi-view Images out
<br>
<p align="center">
    <img src="docs/multiview.gif" width=80%>
    <p align="center">
        <b>Figure 2.</b> <i>Multi-view images rendered using PyBlend with the XYZ Dragon, teapot, and Stanford Bunny.</i>
    </p>
</p>

With PyBlend, you can effortlessly render multi-view images from a single OBJ file. Using the provided command, you’ll be able to generate an impressive set of 30 images. Additionally, you have the option to assign HEX color to the object using the `--color` argument. A big thank you to [Silvia Sellán](https://www.silviasellan.com) for generously sharing her insightful [blog](https://research.siggraph.org/blog/guides/rendering-a-paper-figure-with-blender/)!

```shell
$ blender_app -b -P scripts/multiview.py -- --input docs/bunny.obj --name bunny --num 30

$ blender_app -b -P scripts/multiview.py -- --input docs/dragon.obj --name dragon --num 30 --color 127EB4
```

### 3. Objaverse Extension 🔮

<br>
<p align="center">
    <img src="docs/objaverse.gif" width=800%>
    <p align="center">
        <!-- five pictures: seg, bbox, rgb, normal, depth -->
        <b>Figure 3.</b> <i>Rendering images for Objaverse dataset. Our script provides <b>semantic segmentation (left)</b>, <b>bounding box (middle left)</b>, <b>RGB (middle)</b>, <b>normal map (middle right)</b>, and <b>depth map (right)</b> images.</i>
    </p>
</p>

The [Objaverse](https://objaverse.allenai.org) is an extensive 3D object dataset. To harness the potential of this dataset, we offer a script designed to assemble scenes with informative annotations. The script seamlessly fetches the required objects and orchestrates the rendering of scenes. By executing the following command, you can produce a total of `{num_scene} * {num_views}` images, with `{num_obj}` different objects randomly selected and positioned within each scene:
```shell
$ blender_app -b -P scripts/show_objaverse.py -noaudio -- --num_scene 10 --num_views 2 --num_obj 10
```
Please note that the `-noaudio` flag is included in order to prevent any audio device usage during this process.

## TODO
**Still under development. More functions will be added soon.**

- [x] Add visualization scripts.

- [ ] Add animation and physics simulation functions.

- [x] Add [Objaverse](https://objaverse.allenai.org) extension.

- [ ] Documentation.

## 

## Other Resources
- [Blender Python API](https://docs.blender.org/api/current/index.html)
- [DLR-RM/BlenderProc](https://github.com/DLR-RM/BlenderProc)
- [yuki-koyama/blender-cli-rendering](https://github.com/yuki-koyama/blender-cli-rendering)
- [njanakiev/blender-scripting](https://github.com/njanakiev/blender-scripting)

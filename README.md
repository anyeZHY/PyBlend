# PyBlend

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) **PyBlend is a Python library for [Blender](https://www.blender.org/). It provides a lot of useful functions for Blender scripting.**

<p align="center">
    <img src="docs/teaser.gif" width=810%>
</p>
<br>

## Installation

Setting up the environment for Python in Blender is a challenge. However, following the steps below, you can easily configure the environment.

1. Download Blender from [here](https://www.blender.org/download/).
    
    If your project has high environment requirements, you need to carefully select the version of Blender. Also, there seems to be NO such a version of Blender that supports python 3.8, which could be checked from [blender/tags](https://github.com/blender/blender/tags). Here I use `blender-3.3.1-linux-x64.tar.xz` for Linux users with python 3.10.2.
    Unzip the file and you will get a folder like this:

    ```bash
    ./blender-3.3.1-linux-x64
    ├── blender
    ├── 3.3
    ...
    ```
    where `blender` is the executable file (I will use `{path/to/blender}` or `blender_app` to represent this path in the following) and `3.3` contains the python environment for Blender.

2. Download `get-pip.py` and install pip for Blender python.

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
I recommend you to use `alias blender_app='{path/to/blender}'` to simplify the command.

### Render Normal and Depth Images

Like teaser.gif, you can render normal and depth images with PyBlend. The following command will render 60 images from 0 to 60 degrees.

```shell
$ blender_app -b -P scripts/teaser.py -- --begin 0 --end 60
```

## TODO
**Still under development. More functions will be added soon.**

- [ ] Add visualization scripts.

- [ ] Add instructions for rendering.

- [ ] Add animation and physics simulation functions.

- [ ] Support multi-processing rendering.

- [ ] Add [Objaverse](https://objaverse.allenai.org) extension.
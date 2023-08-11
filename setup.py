from setuptools import setup, find_packages

setup(
    name="pyblend",
    version="1.0",
    description="Python wrapper for Blender",
    author="Haoyu Zhen",
    author_email="anye_zhen@sjtu.edu.cn",
    packages=find_packages(),
    install_requires=["numpy", "objaverse"],
)

from setuptools import setup, find_packages


setup(
    name="pyglet_particles",
    author="sombra-studio",
    version="0.1.0",
    description="particle systems for pyglet",
    license="MIT",
    install_requires=[
        'numpy',
        'pyglet'
    ],
    packages=find_packages(),
    python_requires=">=3.7"
)
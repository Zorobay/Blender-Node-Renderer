# Blender-Node-Renderer
An Addon for Blender that can automatically vary a set of node parameters based on user defined criteria and render each variation.

**This addon is currently under development and is not expected to be stable whatsoever**

## Dependencies

Unfortunately, this addon needs a few external Python modules to take advantage of the parameter optimization feature. To install them, find the python executable that is bundles with blender by executing the following in the Python Console editor inside Blender:

```python
import sys
sys.exec_prefix
```

Start a command window (PowerShell or Git Bash) **as an administrator** and `cd` to that path. From there, execute the following to install the needed modules:

```cmd
./bin/python -m pip install Pillow sklearn numpy
```
## Development
Development is easiest done in VS Code, as the excellent [Blender Development](https://github.com/JacquesLucke/blender_vscode) plugin makes life so much easier when developing. Install it, then setup the *pypredef* so that vs-code can autocomplete the `bpy` module.

### Setup of Pypredef in VS Code

Go to `User Settings` and search for `python auto complete extra paths`. Edit the JSON settings and add 

```
"python.autoComplete.extraPaths": ["PATH/TO/PREDEF"],
```

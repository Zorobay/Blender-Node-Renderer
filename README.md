# Blender-Node-Combination-Renderer
An automatic renderer for Blender that can vary a set of node parameters and render each variation set.

## Setup of Pypredef in VS Code

Go to `User Settings` and search for `python auto complete extra paths`. Edit the JSON settings and add 

```
"python.autoComplete.extraPaths": ["PATH/TO/PREDEF"],
```

## Useful tips and tricks for Blender Addon Development

### Values for bl_xxx

Valid values for `bl_space_type`:

```
('EMPTY', 'VIEW_3D', 'IMAGE_EDITOR', 'NODE_EDITOR', 'SEQUENCE_EDITOR', 'CLIP_EDITOR', 'DOPESHEET_EDITOR', 'GRAPH_EDITOR', 'NLA_EDITOR', 'TEXT_EDITOR', 'CONSOLE', 'INFO', 'TOPBAR', 'STATUSBAR', 'OUTLINER', 'PROPERTIES', 'FILE_BROWSER', 'PREFERENCES')
```
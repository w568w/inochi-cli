# Inochi CLI

Inspect, edit and render Inochi2D models from the terminal.

`inochi` brings model editing to scripts and AI agents: read a model as JSON, change its rig, render the result and use the preview to make the next edit. It works with `.inx` projects and `.inp` models, using Inochi Creator and the Inochi2D SDK v0.8.6.

- **Inspect and edit** nodes, meshes, textures, masks and model metadata.
- **Build rigs** with parameters, key forms, physics, automation and animations.
- **Preview and export** poses, parameter grids, images, texture atlases, INP models and video.
- **Automate edits** with JSON batches, structured output and image-to-model coordinate mapping.

[Quick start](#quick-start) · [Installation](#installation) · [Batch editing](#batch-editing) · [Command reference](#command-reference)

## Quick start

Find the nodes and parameters in your model:

```sh
inochi model.inx node list
inochi model.inx param list
```

Render a preview:

```sh
inochi model.inx render -o preview.png
```

This writes a transparent PNG and `preview.json`, which records the pose, bounds and coordinate transforms. On Linux, previews can run without a desktop through Xvfb; `--software` selects Mesa software rendering.

Move a node and save the edited model:

```sh
inochi model.inx node set --node Face --position=-43,-452 -o edited.inx
inochi edited.inx render --focus Face -o face.png
```

Replace `Face` with a node from your model. Nodes and parameters can be selected by name, full path or UUID. Editing coordinates are local to the node by default; `--space=world` uses model coordinates.

Preview a two-dimensional parameter as a nine-pose grid:

```sh
inochi edited.inx render grid --param Head-Tilt --values=-1,0,1 -o xy.png
```

Use a 2D parameter from your model in place of `Head-Tilt`. Every pose uses the same camera bounds, so the images can be compared directly.

Export a model for playback:

```sh
inochi edited.inx export inp -o model.inp
```

Edits write to the file given by `-o`. Use `--in-place` to overwrite the input.

## Installation

### Build from source

You need CMake 3.24+, Git, Dub, a D compiler and a C++17 compiler, plus the SDL2, FreeType and OpenGL development libraries. CMake downloads the pinned source dependencies during configuration.

From the source directory:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
cmake --build build --config Release --parallel
cmake --install build --config Release
```

Add `--prefix PATH` to the install command to choose the destination. Add its `bin` directory to your `PATH`.

Optional runtime dependencies:

| Feature | Requirements |
| --- | --- |
| Headless rendering on Linux | Xvfb and xauth |
| Software rendering on Linux | Mesa |
| JPEG and video export | FFmpeg |

## Batch editing

Save related operations in `edits.json`:

```json
[
  {"command": "node set", "options": {"node": "Face", "position": [-43, -452]}},
  {"command": "project check"}
]
```

Run the batch against a model:

```sh
inochi model.inx batch edits.json -o edited.inx
```

A batch loads the model once and runs operations in order. Each operation accepts the same options as its command-line equivalent. Outputs are published after the whole batch succeeds; a failure reports the operation index and preserves existing output files.

## Command reference

```sh
inochi --help
inochi model.inx mesh transform --help
inochi capabilities --json
```

Add `--json` to queries for structured output. `capabilities --json` includes the command catalog, supported options and batch JSON Schema. Errors go to stderr and return a nonzero exit code.

For agent workflows, key-form editing and preview coordinates, see [AGENTS.md](AGENTS.md). The [operation coverage table](docs/coverage.md) maps Creator controls and canvas tools to CLI commands.

## Development

The test suite requires Python 3, Pillow, psutil and the runtime dependencies above. Enable it and run:

```sh
cmake -S . -B build -DBUILD_TESTING=ON
cmake --build build --config Release --parallel
ctest --test-dir build -C Release --output-on-failure
```

Create a binary archive with `cpack --config build/CPackConfig.cmake -C Release -G ZIP`.

## License

[BSD-2-Clause](LICENSE). Built on [Inochi Creator](https://github.com/Inochi2D/inochi-creator/tree/v0.8.6) and [Inochi2D](https://github.com/Inochi2D/inochi2d/tree/v0.8.6); see [CONTRIBUTORS.md](CONTRIBUTORS.md) for upstream attribution. Dependency licenses apply to their respective components.

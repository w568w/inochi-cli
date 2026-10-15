# Inochi CLI

Build and install with CMake as described in README.md. The installed `inochi` runs from any working directory. Discover commands and the batch schema through `inochi capabilities --json`, and operation options through `inochi MODEL GROUP ACTION --help`.

## Editing workflow

Inspect `node list`, `param list` and `mesh get --node NAME` with `--json` before editing. Names are case sensitive and ignore trailing NULs; use full paths or UUIDs to resolve duplicate names. Parameters use the model's original value range. Angles are radians.

Edits require `-o OUTPUT.inx`; only `--in-place` overwrites the input. Group related edits in a JSON array of `{"command":"group action","options":{...}}`, then run `inochi MODEL batch edits.json -o OUTPUT.inx`. Commands share their implementations with batch operations. Complex arguments accept JSON, `@FILE` or `-` for stdin. `history begin/end` groups undo steps inside a batch. A failed operation stops the batch and reports its zero-based index without publishing outputs.

Preview the result and inspect the actual image before accepting a visual edit. Use `render --focus NODE` for a crop, `--isolate NODE` for a selected subtree, and `--mesh --vertices` for topology. `render grid --param NAME --values=-1,0,1` renders nine poses with a shared camera. PNG sidecars contain parameter states, world vertices and coordinate transforms. Run `project check` and reload saved models.

## Coordinates and deformation

Coordinates default to node-local pixels. `--space=world` uses model coordinates; `--space=image --reference=preview.json` uses image pixels. Grid references also require `--tile=x,y`. World/image vertex placement uses SDK evaluation to invert MeshGroup deformation.

`mesh transform --node NAME --param PARAM --at=x,y --move=dx,dy` edits a key form. `key set --offsets=@offsets.json` takes one displacement pair per vertex. Scalar keys use `--property=transform.t.x --value=NUMBER`. `key reset` and `key unset` have different meanings. A replacement mesh takes `{"vertices":[[x,y],...],"uvs":[[u,v],...],"triangles":[i,j,k,...]}`. Topology changes remap existing bindings through Creator's implementation.

## Source and verification

`source/cli/registry.d` owns command discovery, help and the batch schema. Keep command behavior in the corresponding operation module. Use SDK/Creator implementations for model semantics. Preserve extension types and vendor sections on save.

Upstream sources are fetched by CMake into its build directory; persistent upstream changes belong in `patches/`. Creator and SDK are pinned to v0.8.6. `ctest --test-dir build --output-on-failure` runs the regression suite serially. Linux without a display uses Xvfb. Tests write only to `tests/results/`. Update `docs/coverage.md` when adding or changing an operation; do not check generated capabilities, schemas or test reports into the repository.

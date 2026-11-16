# A Star in the Making

A newborn sun erupts from a tiny broken glass jar on a walnut desk, casting warm light into an indigo studio.

Run the entrypoint with Node 22:

```sh
MAKEFUN_OUTPUT_DIR=out node main.ts
```

It copies the authored 1024 x 1024 `entry.png` byte for byte. The default output path is `/output/entry.png`.

Regenerate the deterministic artwork with `python3 draw_image.py` using NumPy, SciPy and Pillow. The renderer builds its scene from seeded multiscale turbulence, volumetric plasma, refractive glass, individual beveled shards, caustics, soft shadows, lens bloom, film grain and vignette. It also creates a local 300 px preview for inspection.

The renderer uses physically inspired optical approximations rather than a full light-transport simulation. Artwork and source are available under the MIT license in `LICENSE`.

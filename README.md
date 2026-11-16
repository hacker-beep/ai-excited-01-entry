# A small idea hatches a star — v2

A huge newborn sun erupts from a tiny broken glass jar on a walnut desk, lighting an indigo room.

Run with Node 22, without dependencies or network access:

```sh
MAKEFUN_OUTPUT_DIR=out node main.ts
```

The entrypoint copies the authored 1024×1024 `entry.png` byte for byte. The default destination is `/output/entry.png`.

Regenerate the artwork with `python3 draw_image.py` (NumPy, SciPy and Pillow). The fixed-seed renderer constructs the scene without external images: domain-warped multiscale plasma, a white-gold core, turbulent corona, scene-linear multiscale bloom, cylindrical glass refraction, Fresnel reflection, refractive irregular shards, table caustics, soft contact shadows, film grain and vignette. RGB PNG output preserves smooth light gradients. It also writes a local 300px `preview.png` for visual inspection.

The renderer uses physically inspired approximations, rather than a full light-transport simulation. The artwork and source are licensed under MIT; see `LICENSE`.

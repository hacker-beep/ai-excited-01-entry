# A small idea hatches a star

An original procedural poster for make.fun's **Make the AI judge excited** competition: a newborn sun tears through a desk lightbulb. A white-gold plasma vortex, swept corona, escaping glass and a scattering flock carry the burst toward the upper right.

Run with Node 22, without dependencies or network access:

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out node main.ts
```

The program copies the committed `entry.png` without re-encoding it. Its default destination is `/output/entry.png`.

`draw_image.py` is the development renderer. It uses Pillow and NumPy to construct the entire artwork from geometry, seeded noise, analytical fields and compositing; it reads no source images. These development libraries are not required by the submitted program.

The artwork and source are available under the MIT license in `LICENSE`.

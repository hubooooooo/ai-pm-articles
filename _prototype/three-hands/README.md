# Real 3D line-rendered hands

The hand meshes and kinematic hierarchy are Shadow Hand E3M5 models provided by Shadow Robot Company and distributed through Google DeepMind's MuJoCo Menagerie under Apache-2.0. Full upstream files and license are retained in `vendor/shadow_hand/`.

`prepare_model.py` converts the MJCF articulation and OBJ geometry to local browser data. Geometry is indexed and quantized; joint transforms and perspective rendering remain fully three-dimensional. No third-party service is called by the page.

Build in this directory:

```sh
npm ci
python3 prepare_model.py
npm run build
```

`scene.js` owns the articulated poses, camera, hidden-surface rendering, silhouettes, crease lines, gentle normal shading and lifecycle. The resulting classic bundle works from local HTML and on GitHub Pages.

Open `../hands-3d.html` for the actual homepage preview. Its Chinese headline has restrained English accents, paper texture, green details and a link to the writing section. The index finger middle/distal links and wrists use green outlines while their surfaces retain the paper color. The outline color reads `--accent-art` from the shared `assets/css/palette.css`; a subtle green signal follows the fingertip contact point. There are no visible scene controls. Reduced motion stops autoplay, offscreen/background rendering suspends, and pre-rendered images are shown when WebGL is unavailable.

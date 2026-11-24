# Format guide

[简体中文](FORMAT.md) | [English](FORMAT_EN.md)

Each clip contains only `motion.bvh` and `motion.csv`. The catalog's `frames`, `fps`, `duration_seconds`, and `files` fields provide timing and integrity information.

## BVH: human skeleton

Human skeleton, rooted at `Hips`. Offsets and position channels use centimetres, with Y up. Euler angles use degrees. Current exports use YXZ rotation channels, but readers should follow every joint's CHANNELS declaration. FPS is `1 / Frame Time`.

BVH and CSV represent the same clip, with matching frame counts and timing. Their different skeletons and units mean spatial values cannot be compared column by column. For visualization, convert BVH centimetres to metres and Y up to Z up using `(x, y, z) -> (x, -z, y) / 100`. This is a display-coordinate conversion, not an additional robot retargeting step.

## CSV: G1 motion

Headerless, N rows by 36 columns, Z up. Columns 0–2 contain root XYZ in metres. Columns 3–6 contain root quaternion XYZW. Columns 7–35 contain 29 body/wrist joint angles in radians, without finger joints.

The exact kinematic order is defined by `csv.columns` and `csv.joint_order` in `data/schema.json`. It is not a universal actuator order.

## Timing

Use each clip's actual FPS from the catalog rather than assuming 30 or 60. Frame i occurs at i/fps seconds. The first-to-last timestamp span is `(N-1)/fps`; a sample-hold playback period is `N/fps`. Short and two-frame clips have not been extended or automatically stitched.

The catalog records file SHA-256 and byte sizes. Validation covers catalog integrity, hashes, frame counts, finite values, quaternions, and timing. It is not a dynamics certificate.

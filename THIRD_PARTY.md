# Dependencies and reference material

## Runtime and build dependencies

- **Python** — Python Software Foundation license; installed separately.
- **NumPy** — BSD-3-Clause; installed with `requirements.txt`, not vendored.
- **Dear ImGui v1.92.9b** — MIT, © Omar Cornut; vendored unmodified in
  `third_party/imgui/` (core plus the `osx` and `metal` backends) with its
  `LICENSE.txt`. Source: https://github.com/ocornut/imgui/releases/tag/v1.92.9b
- **Apple SDK frameworks and tools** — AppKit, Metal, MetalKit,
  GameController, CoreGraphics, ApplicationServices, Foundation, Mach, Clang and codesign are supplied
  by macOS / Xcode Command Line Tools. Their licenses are separate from this
  repository's MIT license.

## Reference projects consulted during development

- [jatosm/RobloxExternal-base](https://github.com/jatosm/RobloxExternal-base),
  by Jatos: reference material for feature behavior and session/Explorer ideas.
  That project's custom JATOS BASE LICENSE is **not** the MIT license.
  Its Windows source, binaries, offsets and Lua runtime are not bundled here.
  The macOS Python/Swift/C implementation in this repository is the release
  source; do not treat this repository's license as relicensing that base.
- An old local offset seed credited **upio and Jonah** and linked to
  `notpoiu/roblox-dumper`. That stale third-party table is excluded from this
  release. The published runtime profile uses the locally derived structural
  and same-binary accessor results, not that seed table.

Roblox, its client executable and its assets are not included and are not
covered by this repository's license. WeirdExt is not an official Roblox
project and claims no upstream endorsement.

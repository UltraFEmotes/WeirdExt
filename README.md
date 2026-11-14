# WeirdExt

**An open-source Roblox external for macOS on ARM64 / Apple Silicon.**

**Tested on an ARM device: MacBook Neo.** This is a macOS external, not a
Windows external, Roblox plugin, Lua executor, or injected client modification.
Python handles process memory and session state; a locally compiled Objective-C++
helper draws the overlay, settings and Explorer with Dear ImGui on Metal. A small C helper accelerates
object discovery. The complete release implementation is supplied as source.

The main entry point is **`main.py`**. There are no bundled executables, demo
modes, live-test launchers, self-test modes or test suite in this release.

## Contents

- [Current status](#current-status)
- [Supported platform and client](#supported-platform-and-client)
- [Install](#install)
- [Compile from source](#compile-from-source)
- [Run](#run)
- [macOS permissions](#macos-permissions)
- [Settings and Explorer](#settings-and-explorer)
- [Terminal commands](#terminal-commands)
- [Command-line options](#command-line-options)
- [Leaving and rejoining games](#leaving-and-rejoining-games)
- [Updating client profiles](#updating-client-profiles)
- [Troubleshooting](#troubleshooting)
- [Source layout and architecture](#source-layout-and-architecture)
- [Contributing and license](#contributing-and-license)

## Current status

This is an experimental, version-specific project. A successful compilation or
memory readback is not proof that a gameplay feature works in the live engine.

| Component | Status |
| --- | --- |
| Persistent box ESP, names and distances | Working in reported live use |
| Part-fitted boxes, skeleton, tracers, off-screen arrows | Working in reported live use |
| Health bars, team colors / team check | Working in reported live use; offsets recorded by `probe_offsets.py` |
| Fly | Working in reported live use; writes the solver velocity found by `probe_jump_velocity.py` |
| ImGui menu: sidebar, themes, saved settings, per-feature keybinds, aim key | Working in reported live use |
| Explorer property panel | Implemented |
| Player list with avatars: teleport and spectate | Working in reported live use; offsets from `probe_offsets.py teleport` / `subject` |
| Fast attach (module global chain) | Experimental: chains found so far did not survive a Roblox restart; attach falls back to the sweep |
| Native Visuals / Player / Aim settings | Implemented |
| Explorer | Working in reported live use; snapshots refresh on request |
| Leaving a game and joining another | **Unreliable in reported live use; under investigation** |
| Actual camera FOV for projection | Implemented; no assumed-FOV projection fallback |
| Camera FOV modification | Opt-in; same-binary evidence required |
| Speed and Jump Power modification | Opt-in, experimental; Speed also updates its check field |
| Noclip | Opt-in, experimental; direct character parts only |
| Mouse / Camera aim methods | Working in reported live use; part, priority and sticky target selectable |
| Infinite Jump | Working in reported live use; writes the solver velocity a live probe confirmed |

Movement, physics, FOV writes, fly and aim start disabled on every launch.
Visual, aim-tuning and keybind preferences are saved to
`~/Library/Application Support/WeirdExt/settings.json`; features that write game
memory are never saved.

## Supported platform and client

- **Operating system:** macOS. Windows and Linux are not supported.
- **Architecture:** native ARM64 / Apple Silicon. Intel Macs and Rosetta execution
  are not supported by this release's ARM64 accessor decoder and client profile.
- **Test hardware:** ARM-based **MacBook Neo**.
- **Python:** 3.11 or newer; Python **3.14** is the recommended environment.
- **Native tools:** Clang/Clang++ and the macOS SDK from Xcode Command
  Line Tools, plus macOS's built-in `codesign`.
- **Python dependency:** NumPy; see [`requirements.txt`](requirements.txt).
- **Roblox client profile:** `0.745.0.7451137` only.

The bundled profile is tied to this exact RobloxPlayer binary SHA-256:

```text
8af3f95d347a5283618dd9c17f4a1b02b59982ff699f00cc6f2a195377f2f6b7
```

The reader checks the installed executable's digest and recovered structure.
An automatic Roblox update can invalidate the profile even when the application
still launches normally. Compiling WeirdExt again does **not** update offsets.
There is no automatic compatibility with arbitrary current or future clients.

The MacBook Neo statement describes the project's reported hardware testing,
not verification of every feature on every macOS release. The experimental
write features, including Infinite Jump and Fly, need additional live validation.

## Install

### 1. Install Apple's command-line development tools

In Terminal, run:

```sh
xcode-select --install
```

Complete Apple's installation dialog. If the tools are already installed, macOS
will say so. Verify the selected toolchain:

```sh
xcode-select -p
xcrun --find clang
clang --version
```

The full Xcode application is not required when Command Line Tools supplies a
working Clang and macOS SDK. Install matching tools after a macOS update
if the SDK or compiler stops working.

### 2. Install a native Python

If using [Homebrew](https://brew.sh), install Python 3.14:

```sh
brew install python@3.14
```

Use an ARM-native Homebrew/Python, not an Intel installation running under Rosetta.
The standard Apple Silicon Homebrew prefix is `/opt/homebrew`.

```sh
"$(brew --prefix python@3.14)/bin/python3.14" -c 'import platform,sys; print(sys.version); print(platform.machine())'
```

The architecture must print `arm64`. A native Python 3.11+ from another source
also works with the project requirements; adapt the Python path below.

### 3. Clone the repository

```sh
git clone https://github.com/UltraFEmotes/WeirdExt.git
cd WeirdExt
```

Keep the whole repository together. `main.py` imports `rbxl/` and `dumper/` and
loads the bundled JSON profile relative to its own file, not your current directory.

### 4. Create a virtual environment and install NumPy

From the repository root:

```sh
"$(brew --prefix python@3.14)/bin/python3.14" -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -c 'import numpy,platform; print(numpy.__version__); print(platform.machine())'
```

Install packages and compile as your normal user. Do not run `pip` with `sudo`.
The virtual environment avoids changing the system Python and gives the
privileged launcher an explicit interpreter path.

## Compile from source

### Recommended build

```sh
.venv/bin/python build.py
```

This command does not attach to Roblox or launch the GUI. It:

1. Requires native ARM64 macOS and Python 3.11+.
2. Compiles the Python sources in memory to detect syntax errors.
3. Typechecks `rbxl/overlay.mm` with Clang++ (`-Wall -Wextra`).
4. Checks the C sweeper with Clang's syntax checker.
5. Loads the bundled runtime profile and checks matching camera/movement/physics
   evidence and field constraints.
6. Compiles the overlay helper and the vendored Dear ImGui sources with
   optimization and packages them as
   `WeirdExt.app`.
7. Applies a local ad-hoc code signature using `codesign`.
8. Builds the C sweeper and prints the output paths.

The overlay app is cached at:

```text
.weirdext-native/<source-and-compiler-hash>/WeirdExt.app
```

Its executable is `Contents/MacOS/WeirdExt`. Its bundle identifier is
`dev.weirdext.overlay`. Source and compiler changes produce a new cache identity;
unchanged builds are checked against their recorded source and binary hashes.

The C sweeper is generated at `dumper/sweepc`. Both outputs are ignored by Git.
They are reproducible local build products, not downloads from this repository.

For validation without building executables:

```sh
.venv/bin/python build.py --check
```

These are syntax/type/profile checks, **not** an automated test suite or proof of
live game behavior. The test suite and native self-test modes were removed from
this release. Run `build.py --check` when changing the source.

### What must be compiled?

Python remains source interpreted by your selected interpreter. Objective-C++ and C
are the only native compilation steps. There is no Node, Electron, CMake, Visual
Studio, private SDK, paid dependency or remote compilation service.

For reference, the C compiler command is:

```sh
clang -O2 -o dumper/sweepc dumper/sweepc.c
```

Use `build.py` for the overlay helper rather than compiling a loose executable:
the app bundle, signature and manifest are part of its macOS permission identity.

The launcher also builds missing/outdated native helpers automatically. Building
once as your normal user before launching with `sudo` avoids root-owned build
artifacts and makes compilation errors easier to separate from attach errors.

## Run

1. Open the ARM64 Roblox application normally.
2. Join a game and wait until it is loaded.
3. From the repository root, run:

```sh
sudo "$PWD/.venv/bin/python" "$PWD/main.py" --fps 60
```

Use your account password when Terminal requests it. Password input is normally
invisible. Keep this Terminal session open while WeirdExt runs.

The Python process requests a Mach task port for external memory access. Under
`sudo`, the native UI helper is launched as the original console user using
`SUDO_UID`; the helper is not given a task port. Do not launch from a root login
shell with no graphical console user and expect normal macOS permission behavior.

On startup, the ImGui menu opens over the game and a **WE** item appears in the
macOS menu bar. Press **Right Shift** (with Roblox or the menu focused) or use
**WE → Toggle Menu** to show and hide it. Closing the menu hands focus straight
back to Roblox. While the menu is open it takes the mouse, so close it to play.
Right Shift detection from inside Roblox needs Input Monitoring.

With the menu closed, the transparent overlay is click-through and tracks the Roblox window even when
Roblox is not the foreground application. Aim input remains focus-gated.

### Stop

- Press **Ctrl+C** in the launcher Terminal;
- enter `quit` in that Terminal; or
- choose **WE → Quit WeirdExt**.

On a normal shutdown, controllers attempt conditional restoration of fields
they changed. Restoration is best-effort, not atomic. A detached/invalid old
session is discarded without restoration writes into stale objects. A forced
process kill cannot run normal cleanup.

## macOS permissions

Permissions for the signed native helper are separate from Python's `sudo`
privileges. Approve only the locally built WeirdExt app you intend to run.

### Accessibility: Mouse aim

In **Aim**, press **Allow mouse control…**. Open **System Settings → Privacy &
Security → Accessibility** and enable the built `WeirdExt.app` if requested.
Use the app path printed by `build.py` when adding it manually.

Mouse aiming posts bounded mouse-movement events. Without Accessibility
permission it remains gated. Camera aim is a separate memory-write path and
does not post those mouse-movement events.

### Input Monitoring: keyboard relay

In **Player**, press **Allow keyboard input…**. If macOS requests it, enable
WeirdExt in **Privacy & Security → Input Monitoring**, then restart WeirdExt.
The helper relays focus state, aim-key state, cumulative Space presses and
the Fly keys (W, A, S, D, Space, Left Shift), and polls Right Shift and your
bound hotkeys. Without this permission those keys are not seen.

### Window discovery / Screen Recording

The overlay uses macOS window metadata to follow Roblox. If macOS restricts
window discovery, inspect **Privacy & Security → Screen Recording** (called
Screen & System Audio Recording on some releases) and the relevant app's
permissions. A separate screen/video capture stream is not part of WeirdExt.

Changing the helper source or compiler changes its cached build path and may
require selecting the newly built app or granting permission again. The app is
locally ad-hoc signed, not Developer ID notarized.

## Settings and Explorer

### Visuals

- **ESP**, **Boxes**, **Names**, **Distance**: control visible target markers.
  Boxes are fitted to the character's projected head, hands and feet; the
  **Fallback height / width** sliders apply only when no limbs are readable.
- **Skeleton**: lines between R15 or R6 body parts (reads every part, so it
  costs more per frame than boxes alone).
- **Tracers**: lines from the bottom center to each box.
- **Off-screen arrows**: edge arrows toward players outside the view or behind you.
- **Health bars** and team colors need `Humanoid.Health/MaxHealth` and
  `Player.Team` in the profile; see [Updating client profiles](#updating-client-profiles).
- **Hide teammates**: drops players on your team from ESP and from aim.
- **Center mark**: marks overlay center; it is not proof that camera offsets are
  correct.
- **Show me**: includes the local player.
- **Update rate**: sampling target between 1 and 60 Hz. Native drawing targets
  60 Hz; actual sampling/delivery rates are reported separately.
- **Change FOV**: opt-in game-camera FOV write. Projection always uses the
  camera value read from memory, never the slider as an assumed projection FOV.

### Player

- **Change Speed / Speed**: paired local Humanoid speed/check-field writes.
- **Change Jump / Jump**: local JumpPower and UseJumpPower fields. This is not
  the same feature as Infinite Jump.
- **Noclip**: clears the collision bit on validated direct character parts.
  Nested accessory/tool handles are not comprehensively traversed.
- **Infinite Jump**: on each Space press in the air, writes the Jump value into
  the physics solver's velocity for your character (plus its two mirrors).
  The mirrors alone are overwritten by the next physics step.
- **Fly**: every tick sets the same solver velocity from the camera: WASD moves
  along the view, Space rises, Left Shift sinks, no keys hovers. **Fly speed**
  sets studs per second. Needs Input Monitoring for the keys.

### Aim

Enable **Aimbot**, choose **Mouse** or **Camera**, set **Radius** and
**Smoothness**, focus Roblox and use the aim key.

- **Aim key** (Aim tab): Right Mouse by default. Click it and press any key,
  Option/Command/Control (left or right), Left Shift, or a mouse side button;
  **Esc** resets it to Right Mouse. Handy on a trackpad.
- **Activation**: **Hold** aims while the key is down, **Toggle** flips aiming on
  each press, **Always** aims whenever Roblox is focused.

- **Part**: Head, Torso, or Closest (the visible part nearest the crosshair).
- **Priority**: Crosshair (nearest on screen) or Distance (nearest in the world),
  always within the radius.
- **Sticky target**: keeps the current target while aiming stays active and it
  stays inside the radius.
- Dead players (health 0, when health is in the profile) are skipped, and
  **Hide teammates** also skips teammates.

Mouse mode uses bounded smoothed deltas and requires Accessibility. Camera mode
writes rotation only, with quaternion interpolation; camera translation is not
written. Custom camera scripts, stale state, missing permission and game
behavior can prevent either experimental method from producing the intended result.

### Players

Every other player with a readable character, nearest first, with team color,
distance and health.

- **Teleport** moves you 3 studs above that player: it shifts every physics
  solver position copy and both pose copies together and zeroes your velocity. Needs
  `probe_offsets.py teleport`. Games with server-side movement checks can pull
  you back.
- **Spectate** points the camera's `CameraSubject` at that player's Humanoid;
  **Stop** restores yours. It copies the target's full smart-pointer pair and
  adds one reference first, so a respawn that resets the camera cannot free a
  live object (one reference leaks instead). It ends on its own when the target
  leaves or respawns, or when Roblox changes the camera itself. Needs
  `probe_offsets.py subject` (read-only).

### Keybinds

Click a feature in the **Keybinds** tab and press a key, Option/Command/Control,
or a mouse side button to bind it; **Esc** clears the binding. Bound keys toggle
ESP, Aimbot, Fly, Noclip, Infinite Jump or Speed while Roblox is focused.
**Right Shift** always toggles the menu. Bindings are saved with your settings.

### Theme

Pick an accent (Violet, Crimson, Ocean, Emerald, Amber, Rose, Mono) and a
background (Graphite, OLED, Slate); the accent also colors ESP boxes, arrows and
the watermark. The **Watermark** switch hides the top-left status pill. Nothing
is drawn unless Roblox or the menu is the active app.

### Explorer

Open **WE → Explorer…** or the **Explorer** tab. Opening it requests one bounded,
read-only tree snapshot. Use the search field to filter it and **Refresh** to
request a new snapshot. Click a node to see its name, class, address, parent
address and child count; **Copy** puts a value on the clipboard.

Snapshots are capped at 2,000 nodes, depth 8, 64 children per node and a four-second
budget. Large trees can be truncated. Snapshot construction can briefly reduce
sampling performance. Refresh after a rejoin to inspect the new game's tree.

## Terminal commands

Type these into the running launcher's Terminal and press Return:

| Command | Effect |
| --- | --- |
| `fov 80` | Enable a game-camera FOV request; allowed range 30–120 degrees |
| `fov auto` or `fov reset` | Disable the override and attempt conditional restoration |
| `basis flip` | Switch projection interpretation between rows and columns |
| `basis rows` / `basis columns` | Select the projection interpretation explicitly |
| `inset 28` | Set the overlay's windowed top/title-bar inset in points |
| `pos 0 -10` | Set overlay x/y offsets in screen points |
| `quit` | Stop WeirdExt |

These are WeirdExt controls, not a general command executor. Fullscreen tracking
uses zero title-bar inset. Calibration changes do not validate an offset profile.

## Command-line options

Run `.venv/bin/python main.py --help` for the authoritative option list.

| Option | Default / meaning |
| --- | --- |
| `--fps 60` | Sampling target, 1–60 Hz |
| `--pid 1234` | Initial Roblox PID; otherwise select the largest matching client process |
| `--profile DIR` | Profile directory; default: the one under `profiles/` whose SHA-256 matches the installed RobloxPlayer |
| `--diagnostics` | Verbose per-target camera/projection diagnostics |
| `--inset-top 28` | Initial windowed inset, 0–100 points |
| `--show-local` | Initially include the local player |
| `--box-height 5.4` | Fallback box height when no limbs are readable, 1–20 studs |
| `--box-ratio 0.6` | Fallback width/height ratio, 0.2–2 |
| `--headless` | No native UI/overlay; print projected state |
| `--seconds 10` | Stop after this many seconds of the polling loop; 0 runs until stopped |
| `--width 1280 --height 720` | Positive headless/fallback viewport dimensions |

For headless inspection:

```sh
sudo "$PWD/.venv/bin/python" "$PWD/main.py" --headless --seconds 10
```

Headless mode still attaches to the real client. It is not a synthetic mode and
has no GUI settings/input helper. Discovery/startup time is outside the polling
duration. `--pid` selects the initial process; recovery can discover a replacement
Roblox PID rather than remaining pinned to an exited process.

## Leaving and rejoining games

Leave WeirdExt running when exiting a game or joining another one. Recovery
checks service ownership and sustained incomplete frames rather than relying on
old addresses still having readable vtables.

During a transition:

1. Invalid old controller bindings are discarded and writes pause.
2. A single background worker performs fresh discovery, bypassing the old object
   census. Failed attempts retry after completion, normally two seconds apart.
3. Settings and quit handling remain available; there is no five-minute retry cutoff.
4. A newly discovered PID is handed to the native helper for window/focus tracking.
5. A valid frame resumes normal updates and produces:

```text
[session] Reconnected — game loaded; updates resumed
```

Physics status messages are logged when their active status changes, not as a
repeated `[physics] Waiting for game` heartbeat. An “updates resumed” message is
about the connection, not a claim that every experimental write feature works.

## Updating client profiles

`main.py` picks the profile under `profiles/` whose recorded SHA-256 matches the
installed `/Applications/Roblox.app/Contents/MacOS/RobloxPlayer`. After a Roblox
update, join a game and build a new one:

```sh
sudo "$PWD/.venv/bin/python" "$PWD/update_profile.py"
```

It reads geometry, camera, movement and physics getters from the binary
offline, runs one live discovery for the instance layout, writes
`profiles/<version>-<sha8>/`, and validates it with the same loaders `main.py`
uses. It never overwrites a profile. It then looks for a global in the client's
data segments that leads to the live DataModel within two pointer hops,
attaches through it to prove it, and records it as `fast_attach`. Run against a
client that already has a matching profile, it adds only that chain. With
**fast attach**, attaching takes a few reads instead of a ~50 s heap sweep; if
the chain ever stops resolving, attach falls back to the sweep. Chains found so
far were session-specific (they broke after restarting Roblox), so the bundled
profile ships without one.

Live-only fields come from their own probes, run in a game (each writes into
the matching profile only when exactly one candidate survives):

```sh
sudo "$PWD/.venv/bin/python" "$PWD/probe_jump_velocity.py"   # solver velocity: Infinite Jump, Fly
sudo "$PWD/.venv/bin/python" "$PWD/probe_offsets.py" team     # Player.Team: team colors, team check
sudo "$PWD/.venv/bin/python" "$PWD/probe_offsets.py" health   # Humanoid.Health/MaxHealth: health bars
sudo "$PWD/.venv/bin/python" "$PWD/probe_offsets.py" subject  # CameraSubject + WeakThis: spectate (read-only)
sudo "$PWD/.venv/bin/python" "$PWD/probe_offsets.py" teleport # solver position: teleport (lifts you 10 studs)
```

`probe_jump_velocity.py` writes to candidate memory during falls; use a
throwaway server. `probe_offsets.py health` asks you to take damage a few times.

The lower-level tools remain for inspection: `inspect_*_accessors.py` (offline,
`--json` never overwrites) and `dump_offsets.py` (live structural report).
Leave write features off while validating a new build. Local reports can contain
process addresses and memory-derived samples; do not publish them wholesale.

## Public offset dumps

`export_offsets.py` turns the profile matching your installed client into a
shareable dump, without opening Roblox:

```sh
.venv/bin/python export_offsets.py
```

It writes `dumps/<version>/offsets.hpp`, `offsets.cs` and `offsets.json`,
grouped as `Namespace::Name` like common Windows dumps, with the client
version, binary SHA-256 and dump time in the header. Two sources are merged:

- **Confirmed live**: the profile's offsets (probes and live use).
- **Reflection** (`dumper/reflection.py`, offline): every property Roblox
  registers with its reflection system has a name, a getter and a descriptor
  whose RTTI names the class and value type. Getters that decode to an exact
  instruction shape (a single load, a reference return, a string, a smart
  pointer, ...) become offsets: about 2,300 properties across 360 classes for
  0.745. Reflected values that overlap confirmed ones must match exactly or the
  export stops. Properties read through another object (e.g. BasePart physics
  values on the Primitive) are commented `at *(object + X) + this`.

Getters that only decode heuristically go to `unverified.json` instead of the
headers; confirm them live before relying on them.

**Live check (recommended before publishing).** In any game:

```sh
sudo "$PWD/.venv/bin/python" "$PWD/verify_offsets.py"
.venv/bin/python export_offsets.py
```

`verify_offsets.py` samples real instances of each class (and subclasses, via
RTTI), reads every property where the dump says it is, and fails values that
cannot be that type (bools not 0/1, non-finite floats, references that are not
Instances, unreadable strings, CFrames that are not rotations). The export then
drops reflected offsets that failed and promotes heuristic ones that passed. It
also finds `DataModel` PlaceId / JobId (from Roblox's own log), GameId /
CreatorId (Roblox web API for that place) and `Player` UserId (web API for your
username) by searching for those exact values. Plausibility is evidence, not
proof: a wrong offset can still hold a plausible value. It only reads. These are **macOS ARM64** values: struct
layouts differ from the Windows client. The `SolverBody` namespace has no
Windows equivalent: it is the physics body that actually moves a part (its
`AssemblyLinearVelocity` in `Primitive` is a copy refreshed every step).

After a Roblox update: `update_profile.py`, the probes, then `export_offsets.py`.

## Troubleshooting

### `task_for_pid(...) failed`

Use the explicit `sudo` launcher command. Root privileges do not guarantee that
macOS will grant a task port: hardened processes or platform restrictions can
still deny it. WeirdExt does not provide a platform-protection bypass. Do not
change machine security settings based on assumptions about this error.

### `installed binary differs from offset report`

The installed executable does not match the selected profile. Rebuilding the
native helpers cannot solve a client-version mismatch; run `update_profile.py`
(see [Updating client profiles](#updating-client-profiles)). `no profile matches
the installed Roblox` at startup means the same thing.

### Discovery reports no loaded session / no self-named instance

Ensure a game has loaded, not just the launcher or home screen. Initial PID
selection uses process footprint; use `--pid` if that selected the wrong process.
Recovery bypasses the cached census, but cannot recover objects that do not yet
exist or use a layout unsupported by the decoder.

### No overlay or misaligned boxes

Check that **ESP** and **Boxes** are enabled, the camera FOV is readable, the
native helper is running and Roblox has a visible window. Inspect permission and
window-availability messages. Use `--diagnostics`, `inset`, `pos` and `basis`
controls to investigate alignment. A center mark aligned to the crosshair does
not prove the camera/geometry profile is correct.

### Infinite Jump or Fly does nothing

`[physics]` messages distinguish missing keyboard input, missing Input
Monitoring, lost focus and a refused write. `solver body offsets not in profile`
means the profile lacks the solver entry: run `probe_jump_velocity.py`.
`solver body velocity does not match the part` means the recorded solver offset
no longer tracks this build; rerun the probe.

### Native cache integrity error / permission prompts return

Cached executables are verified. Do not modify them in place. Change the overlay
source and build normally to produce a new cache identity, or identify the
specific damaged cache entry before removing it and rebuilding. A new helper
path/signature may need a new permission approval. Do not recursively delete the
repository to resolve a build-cache error.

### Build outputs are owned by root

This can happen when the initial compilation was performed through `sudo`.
Inspect ownership of `.weirdext-native/` and `dumper/sweepc`. Repair only those
generated outputs as appropriate for your account, then run `build.py` as your
normal user. Never install Python packages globally with `sudo pip` to fix it.

### `ModuleNotFoundError: numpy`

Use the same virtual-environment interpreter for installation and launch:

```sh
.venv/bin/python -m pip install -r requirements.txt
sudo "$PWD/.venv/bin/python" "$PWD/main.py"
```

### Some features are disabled or reset after restart

Movement, physics and FOV controls require matching evidence and supported
objects. Disabled controls can indicate a missing controller/evidence file.
Features that write game memory always start off; preferences and keybinds are
restored from `~/Library/Application Support/WeirdExt/settings.json`.

## Source layout and architecture

```text
main.py                         Main launcher, controls and frame/session loop
build.py                        Local build and static/profile validation
requirements.txt                NumPy dependency
rbxl/
  overlay.mm                    ImGui/Metal overlay, menu, hotkeys, saved settings, Explorer
  profiles.py                   Profile selection by installed binary SHA-256
  spectate.py                   CameraSubject spectate with balanced reference counts
  native_build.py               Content-addressed overlay app build/signing
  memory.py                     Mach reads, process selection, task-port lifecycle
  esp_reader.py                 ESPReader, ownership checks and fresh snapshots
  esp_settings.py               Strict shared settings contract
  w2s.py                        Camera/world-to-screen projection
  aim.py, camera_aim.py          Target selection and Camera aim
  camera_control.py             Opt-in camera FOV writes/restoration
  movement.py                   Paired Speed/check and JumpPower transactions
  physics_control.py            Noclip, Infinite Jump and Fly (solver velocity writes)
  input_state.py                Input validation and receiver-clock freshness
  session.py                    Session health, worker recovery and roster feed
  explorer.py                   Bounded read-only tree snapshots
dumper/
  macho.py, rtti.py              Mach-O parsing and Itanium RTTI resolution
  solve.py, derive.py            Structural discovery and field derivation
  scan.py, sweepc.c              Python/native discovery scans
  *_accessors.py                Offline ARM64 property/accessor decoders
  prims.py, snapshots.py         Structural and sample-validation helpers
  emit.py                       New report/table output
dump_offsets.py                 Live structural report CLI
update_profile.py               Build/extend a profile for the installed client
probe_jump_velocity.py          Live probe: solver velocity for Infinite Jump/Fly
probe_offsets.py                Live probes: team, health, camera subject, teleport position
inspect_*_accessors.py           Offline executable inspection CLIs
profiles/0.745.0.7451137/         Sanitized version/hash-bound runtime summaries
third_party/imgui/              Vendored Dear ImGui v1.92.9b (MIT) + osx/metal backends
LICENSE                         MIT license
THIRD_PARTY.md                  Dependencies and research references
```

The UI communicates over newline-delimited JSON stdin/stdout. Its bounded
latest-frame mailbox avoids rendering an accumulating backlog. Geometry poses
and ownership links are reread; old positions are not a general fallback for
failed reads. Controller writes are separate Mach operations with validation
and best-effort rollback, not atomic engine property setters.

All source required for the release is published. `.gitignore` intentionally
allows the release tree and excludes historical dumps, private snapshots, local
scratch scripts, obsolete readers/seeds, build outputs, virtual environments,
machine-specific agent configuration and Python caches.

## Contributing and license

Fork the repository, create a branch, make a focused change and run:

```sh
.venv/bin/python build.py --check
.venv/bin/python build.py
```

State separately what you compiled, what you observed live, the hardware and
macOS version, client version/hash and relevant status output. Do not claim a
feature works solely because a field's memory readback matched. Keep private
memory captures, client executables and credentials out of commits and issues.

The release source is licensed under **MIT**; see [`LICENSE`](LICENSE).
Dependencies and consulted reference projects retain their own licenses; see
[`THIRD_PARTY.md`](THIRD_PARTY.md). Roblox's executable and assets are not
distributed here. Contributions must be compatible with the repository license.

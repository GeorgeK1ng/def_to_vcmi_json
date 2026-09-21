# 🧩 DEF to VCMI JSON Converter

This tool converts **Heroes of Might and Magic III `.def` and `.d32` files** into a format compatible with **VCMI**. It extracts all image frames (normal, shadow, overlay) and generates a `.json` metadata file usable by VCMI mods.

---

## 🔧 Features

- Extracts all images from `.def` and `.d32` files (normal, shadow, overlay)
- Saves each frame as a `.png` file
- Generates a `.json` file with metadata in VCMI format
- Supports:
  - GUI-based file selection (for quick use)
  - Command-line usage for automation and scripting
  - Optional VCMI object-template and mask generation
  - Optional standalone executable (no Python required)

---

## 🚀 Usage

### Option 1: GUI mode

Run:

```bash
python def2json.py
```

Select one or more `.def` files using the file dialog. The tool will:

- Create a subfolder with extracted PNGs (named after the `.def` file)
- Generate a `.json` file in the same directory

### Option 2: Command-line mode

```bash
python def2json.py path/to/file.def [another.def ...]
```

This will process the provided `.def` files directly, without showing any GUI.

### Command-line options

| Option | Description |
| --- | --- |
| `--onlyconfig` | Write the animation JSON without exporting PNG files. |
| `--ignorefilename` | Generate sequential output names instead of using source frame names. |
| `--ignoregroup` | Use group `0` in generated output names. |
| `--mergeshadow` | Export the library's combined normal/shadow image for DEF frames. |
| `--overlay` | Derive an overlay PNG from opaque yellow and green pixels if no overlay exists. |
| `--vcmi-template` | Generate `NAME.template.json` with a VCMI mask. |
| `--template-frame N` | Use zero-based source frame `N` for the template. Failed frames do not renumber later frames. |
| `--maskonly` | Generate only the template, using temporary frame images. Requires `--vcmi-template` and cannot be combined with `--onlyconfig`. |

For example:

```bash
python def2json.py --mergeshadow --vcmi-template --template-frame 0 object.def
```

Errors from command-line runs are printed and written to `def2json.log` in the
current working directory; they do not open GUI error dialogs.

---

## 📁 Output Structure

For a file named `example.def`, this tool will create:

```
example/                 # Folder with all image frames
  frame1.png
  frame1-shadow.png
  frame1-overlay.png
  ...
example.json             # JSON metadata for VCMI
```

For D32 input, the JSON uses group `0` and a global frame index across source
groups. This is intentional because D32 frames are represented as one sequence
in the generated VCMI animation.

---

## 📦 Using in VCMI

To use in a VCMI mod:

1. Copy the `example/` folder and `example.json` into the `sprites/` folder of your mod.
2. If placing inside a subfolder (e.g. `sprites/myfolder/example/`), update the `basepath` in the `.json` accordingly:

```json
{
    "basepath": "myfolder/example/",
    ...
}
```

---

## 📥 Requirements

You can use this tool in two ways:

### ✅ Option 1: Python script

- Requires Python 3
- Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

Then run:

```bash
python def2json.py
```

### ✅ Option 2: Standalone executable

If you don't have Python installed, use the provided standalone executable:

- No installation needed
- Just double-click or run from command line:

```bash
./def2json.exe          # on Windows
./def2json              # on Linux/
```

### Windows 7 and Windows XP

The GitHub Actions workflow publishes `def2json-win7-x64.exe` and
`def2json-win7-x86.exe` artifacts built with Python 3.8.10. Use the x86
artifact on 32-bit Windows 7.

It also publishes **`def2json-win-xp-x86.exe` for 32-bit Windows XP SP3** and
**`def2json-win-xp-x64.exe` for Windows XP Professional x64 Edition SP2**. Both
use the final XP-compatible Python and PyInstaller toolchain, with all
dependencies frozen in `requirements-xp.txt`. The x86 artifact also runs under
WOW64 on 64-bit Windows; use the x64 artifact only when a native 64-bit process
is required. The CI smoke tests verify that both packaged programs start, but
the artifacts should additionally be tested on matching real XP installations
or VMs before a release.

All targets, including both XP builds, use the same current `homm3data`
version. Its version is defined only once in `requirements-homm3data.txt` and
each CI job verifies the installed version before compiling. When updating
`homm3data`, change that single file so no legacy artifact is left on an older
DEF/D32 parser.

The Windows jobs run on GitHub's maintained `windows-latest` build host. This
is only the machine which performs the compilation; compatibility of the
resulting executables is determined by the explicitly installed Python and
packaging toolchains above, not by naming the CI host after the target OS.

To reproduce an XP build, install the matching 32-bit or 64-bit Python 3.4.4
and run (replace the installation path and output name with the x64 variants
when building for XP x64):

```bat
C:\Python34\python.exe -m pip install --upgrade pip==19.1.1 setuptools==43.0.0
C:\Python34\python.exe -m pip install -r requirements-xp.txt
C:\Python34\Scripts\pyinstaller.exe --onefile --console --name def2json-win-xp-x86 def2json.py
```

To reproduce a Windows 7 build locally, install 32-bit or 64-bit Python 3.8.10
on Windows and run:

```bat
py -3.8 -m pip install -r requirements-win7.txt
py -3.8 -m nuitka def2json.py --standalone --onefile --enable-plugin=tk-inter --output-dir=build --windows-console-mode=attach --assume-yes-for-downloads
```

# Unified Diff Patcher

A standalone Python3 utility to apply **unified diff** patches (`.patch` or `.diff`) to original files and create **numbered backup files** instead of overwriting them.

Example:
```
program.py → program.001.py → program.002.py → ...
```

Unlike `git apply` or `patch`, this tool:
- Works without Git or Unix tools.
- Creates **new numbered files** for each patched version (safe, non-destructive).
- Handles **multiple files** in a single patch.
- Supports **Windows**, **Linux**, and **macOS**.
- Includes **dry-run** mode and **verbose** mode.
- Supports `--base-dir` to patch files in a different folder.

---

## ✅ Features

- **Multiple files in one patch**  
- **Dry-run mode** (`--dry-run`)  
- **Verbose mode** (`--verbose`) for detailed hunk application  
- **Base directory support** (`--base-dir PATH`)  
- **Safe numbering scheme** for output files (`file.001.py`, `file.002.py`, etc.)  
- **Summary report** at the end  
- **Improved error handling** for malformed patches  
- **Windows Batch wrapper** for easy use  

---

## ✅ Requirements

- **Python 3.6+**
- Works on **Windows**, **Linux**, and **macOS**.

---

## ✅ Installation

Just download:
- `unified_diff_patcher.py`
- `ApplyPatch.bat` (optional for Windows users)

No additional libraries required.

---

## ✅ Usage

### Apply a patch in the current directory:
```bash
python unified_diff_patcher.py changes.diff
```

### Preview without creating files (dry-run):
```bash
python unified_diff_patcher.py changes.diff --dry-run
```

### Verbose dry-run (show hunks and changes):
```bash
python unified_diff_patcher.py changes.diff --dry-run --verbose
```

### Apply patch to files inside a specific folder:
```bash
python unified_diff_patcher.py changes.diff --base-dir "./src"
```

### Apply patch in Windows with batch file:
```cmd
ApplyPatch.bat changes.diff --dry-run --verbose --base-dir "C:\MyProject"
```
You can also **drag and drop** the `.diff` file onto `ApplyPatch.bat`.

---

## ✅ Example Output

```
[OK] Patched 'src/program.py' -> 'src/program.001.py'
[SKIP] Original file 'src/otherfile.py' not found.
[ERROR] Failed to apply patch to 'src/main.py': Invalid hunk header: @@ -10,7 +10,9 @@

Summary:
  Files processed: 3
  Patched:         1
  Skipped:         1
  Errors:          1
```

---

## ✅ Notes

- The script **does not overwrite original files**; it always creates a numbered copy.
- If the original file does not exist, the patch is **skipped**.
- Handles standard Git-style prefixes (`a/`, `b/`).
- Malformed patches will **not stop the script**; errors are logged.

---

## ✅ License
MIT License

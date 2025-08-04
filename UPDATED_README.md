# Unified Diff Patcher

A robust Python-based utility for applying unified diff patches (`.patch` or `.diff` files) to source files, now also available as a **standalone Windows EXE** for users without Python installed.

![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-lightgrey) ![License](https://img.shields.io/badge/license-AGPL--3.0-green)

---

## Overview

Unified Diff Patcher applies unified diff patches to original files and creates numbered output files (e.g., `program.py` → `program.001.py`). It works like `git apply` while preserving original line endings and handling complex edge cases.

Now you can **download and run it as a single `.exe` file** without installing Python.

This tool only runs on Windows 10+.    

---

## Foreward

Drafted by ChatGPT AI (with substantial logic errors), fixed and extended by Claude AI.    

Although both Claude AI and ChatGPT AI both can and do make mistakes when in programming python, Claude AI seems to make fewer mistakes and fixes them well when asked.    

Funnily enough, Claude AI found in program comments "Author: ChatGPT" and added "(Enhanced by Claude)" to that comment.    

Both AIs are hampered in the sense that the free plans ate extremely limited in that they
do not let you iterate development much due to their analyses and output limits
... however, even when subscribing to the first level plans the limits
are still substantial enough to impede development, but you can get stuff done.    

For the moment, appreciating both AIs, I applaud Claude.

---

## Download

### ✅ [**Download the latest Windows EXE here**](https://github.com/hydra3333/unified_diff_patcher/releases/latest/download/unified_diff_patcher.exe)

- This is a **self-contained EXE** built using **PyInstaller**.
- No Python installation or external dependencies required.
- Works on **Windows 10 and 11**.


### ✅ [**Alternatively, download the latest release to obtain the raw python `Unified_Diff_Patcher.py`**]

- `Unified_Diff_Patcher.py` uses the same comandline options as the **self-contained EXE**.
- Works in **Python 3.13.5+**.

---

## Running the standalone EXE (`Unified_Diff_Patcher.py` uses the same comandline options)

Open **Command Prompt** in the folder with your patch file and run:

```cmd
unified_diff_patcher.exe patchfile.diff
```

---

### Command-Line Options ()

| Option           | Description                                        |
|------------------|----------------------------------------------------|
| `patchfile`      | Path to the `.diff` or `.patch` file (required)   |
| `--dry-run`      | Show what would happen without making changes      |
| `--verbose`      | Show detailed hunk processing information          |
| `--base-dir PATH`| Base directory where original files are located    |

---

### Usage Examples

Apply patch in current directory:
```cmd
unified_diff_patcher.exe changes.diff
```

Preview changes without applying:
```cmd
unified_diff_patcher.exe changes.diff --dry-run
```

Apply patch to files in specific directory:
```cmd
unified_diff_patcher.exe changes.diff --base-dir "C:\path\to\files"
```

Verbose dry-run for debugging:
```cmd
unified_diff_patcher.exe changes.diff --dry-run --verbose
```

---

## Key Features

### Core Functionality
- **Git-style compatibility**: Handles standard git diff formats with `a/` and `b/` prefixes
- **Multiple file support**: Apply patches to multiple files in one go
- **Empty file support**: Uses system default line endings for empty files
- **Numbered output files**: Creates auto-numbered patched files eg `file.001.ext`, `file.002.ext`, etc. without overwriting any existing files
- **Cross-platform patch file compatibility**: Handles patches created on different OSes i.e. different styles of line endings
- **Line ending intelligence**: Preserves source file style line endings (Windows, Unix, Mac) regardless of patch file style
- **Comprehensive error handling**: Graceful handling of malformed patches and missing files
- **Dry-run mode**: Preview changes before applying

### Edge Case Support
- **Empty files**: Adding content to completely empty files
- **Single-line files**: Replacement and modification of single-line files
- **No trailing newlines**: Files that don't end with newline characters
- **Multiple hunks**: Multiple separate changes within the same file
- **Complex operations**: Mixed add/delete/replace operations in single hunks
- **Whitespace-only changes**: Precise handling of spaces and tabs
- **Large context hunks**: Hunks with many surrounding context lines

---

## Installation Requirements
- **EXE version:** No requirements (self-contained)
- **Python script version:** Python 3.13+ (if running from source) with no external dependencies (uses only Python standard library)

---

## Technical Details

### Algorithm Overview
1. **Parse patch file**: Extract file headers and hunks
2. **Detect line endings**: Analyze source file's line ending style
3. **Apply hunks sequentially**: Process each hunk with offset tracking
4. **Convert line endings**: Ensure output matches source style
5. **Write numbered output**: Create new file without overwriting original

### Error Handling
- **Malformed patches**: Clear error messages for invalid hunk headers
- **Missing files**: Continues processing other files with warnings
- **Context mismatches**: Warnings when patch context doesn't match source
- **Out-of-bounds operations**: Prevents crashes from invalid hunk ranges

### Performance Characteristics
- **Memory efficient**: Processes files line-by-line without loading entire files
- **Fast processing**: Optimized for typical patch sizes
- **Minimal dependencies**: Uses only Python standard library

---

## Limitations and Considerations

### Current Limitations
- **Text files only**: Designed for text-based patches, not binary files
- **UTF-8 encoding**: Assumes UTF-8 encoded files
- **Sequential processing**: Processes files one at a time (not parallel)

### Best Practices
- **Test with --dry-run**: Always preview changes before applying
- **Use --verbose**: For debugging complex patches
- **Backup important files**: Although originals aren't modified, backups are recommended
- **Verify context**: Ensure patches match the intended file versions

---

## Examples of Supported Patch Operations

### Adding Lines
```diff
@@ -1,3 +1,4 @@
 Existing line 1
 Existing line 2
+New inserted line
 Existing line 3
```

### Deleting Lines
```diff
@@ -1,3 +1,2 @@
 Keep this line
-Delete this line
 Keep this line too
```

### Replacing Lines
```diff
@@ -1,3 +1,3 @@
 Context line
-Old content
+New content
 More context
```

### Complex Mixed Operations
```diff
@@ -1,5 +1,4 @@
 Keep line 1
-Delete line 2
-Delete line 3
+Replace with single line
+Add new line
 Keep line 5
```

---

## Example Output and Feedback

### Standard Output
```
[OK] Patched 'file.txt' -> 'file.001.txt' [line ending: '\r\n']
[SKIP] Original file 'missing.txt' not found.
[ERROR] Failed to apply patch to 'broken.txt': Context mismatch

Summary:
  Files processed: 3
  Patched:         1
  Skipped:         1
  Errors:          1
```

### Verbose Output
```
[PROCESSING] file.txt
  Original file has 3 lines
  Detected source line ending: '\r\n'
  Detected patch line ending: '\n'
  NOTE: Patch and source have different line endings - output will match source
    Applying hunk: @@ -1,3 +1,4 @@
      Old: start=1, count=3
      New: start=1, count=4
      Applying at index 0 with offset 0
        Line 1
        Line 2
        Line 3
      + Line 4
      Replacing 3 lines at index 0 with 4 lines
  Patched file has 4 lines
```

---

## Troubleshooting

### Common Patching Issues

**"Hunk cannot be applied"**
- Patch may be for different version of file
- Check that line numbers and context match
- Use `--verbose` to see detailed hunk information

**"Context mismatch" warnings**
- Patch context doesn't exactly match source file
- Often still applies successfully
- Review output file to verify correctness

**"File not found" errors**
- Check `--base-dir` parameter
- Verify file paths in patch match actual file locations
- Ensure files exist and are readable

### Debug Mode
Use `--verbose --dry-run` to see exactly how patches would be applied:
```cmd
unified_diff_patcher.exe problem.patch --verbose --dry-run
```

---

## License
This tool is available only under the AGPL-3.0 license.


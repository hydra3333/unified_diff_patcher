# Unified Diff Patcher

A robust Python utility for applying unified diff patches (.patch or .diff files) to source files, with intelligent line ending preservation and edge case handling.

![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-lightgrey) ![License](https://img.shields.io/badge/license-AGPL--3.0-green)

## Overview

This tool applies unified diff patches to original files and creates numbered output files (e.g., `program.py` → `program.001.py`). It's designed to work like git's patch command while preserving the original file's line ending style and handling complex edge cases.    

This tool only runs on Windows 10+.

## Foreward

Drafted by ChatGPT AI (with substantial logic errors), fixed and extended by Claude AI.    

Although both Claude AI and ChatGPT AI both can and do make mistakes when in programming python, Claude AI seems to make fewer mistakes and fixes them well when asked.    

Funnily enough, Claude AI found in program comments "Author: ChatGPT" and added "(Enhanced by Claude)" to that comment.    

Both AIs are hampered in the sense that the free plans ate extremely limited in that they
do not let you iterate development much due to their analyses and output limits
... however, even when subscribing to the first level plans the limits
are still substantial enough to impede development, but you can get stuff done.    

For the moment, appreciating both AIs, I applaud Claude    

## Key Features

### Core Functionality
- **Multiple file support**: Apply patches to multiple files in a single operation
- **Numbered output files**: Creates `file.001.ext`, `file.002.ext`, etc. without overwriting originals
- **Dry-run mode**: Preview changes without modifying files
- **Git-style compatibility**: Handles standard git diff formats with `a/` and `b/` prefixes
- **Comprehensive error handling**: Graceful handling of malformed patches and missing files

### Line Ending Intelligence
- **Automatic detection**: Detects Windows (`\r\n`), Unix (`\n`), and Mac (`\r`) line endings
- **Preservation**: Output files maintain the original file's line ending style
- **Cross-platform compatibility**: Unix patches work on Windows files (and vice versa)
- **Mixed file handling**: Uses dominant line ending style in files with mixed endings
- **Empty file support**: Uses system default line endings for empty files

### Edge Case Support
- **Empty files**: Adding content to completely empty files
- **Single-line files**: Replacement and modification of single-line files
- **No trailing newlines**: Files that don't end with newline characters
- **Multiple hunks**: Multiple separate changes within the same file
- **Complex operations**: Mixed add/delete/replace operations in single hunks
- **Whitespace-only changes**: Precise handling of spaces and tabs
- **Large context hunks**: Hunks with many surrounding context lines

## Installation & Prerequisites

### Requirements
- Python 3.6 or later
- No external dependencies (uses only Python standard library)

### Files Needed
- `unified_diff_patcher.py` - The main patcher script
- `run_unified_diff_patcher_TESTS.py` - Comprehensive test suite (optional)

## Usage

### Basic Usage
```bash
python unified_diff_patcher.py patchfile.diff
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `patchfile` | Path to the .diff or .patch file (required) |
| `--dry-run` | Show what would happen without making changes |
| `--verbose` | Show detailed hunk processing information |
| `--base-dir PATH` | Base directory where original files are located |

### Usage Examples

#### Apply patch in current directory
```bash
python unified_diff_patcher.py changes.diff
```

#### Preview changes without applying
```bash
python unified_diff_patcher.py changes.diff --dry-run
```

#### Apply patch to files in specific directory
```bash
python unified_diff_patcher.py changes.diff --base-dir "./src"
```

#### Verbose dry-run for debugging
```bash
python unified_diff_patcher.py changes.diff --dry-run --verbose
```

#### Windows path example
```bash
python unified_diff_patcher.py changes.diff --base-dir "C:\path\to\files"
```

## Supported Patch Formats

### Standard Unified Diff Format
```diff
--- a/file.txt
+++ b/file.txt
@@ -1,3 +1,4 @@
 Line 1
 Line 2
 Line 3
+Line 4
```

### Multiple Files in Single Patch
```diff
--- a/file1.txt
+++ b/file1.txt
@@ -1,2 +1,2 @@
-Old line
+New line
 Context line

--- a/file2.txt
+++ b/file2.txt
@@ -1,3 +1,4 @@
 Line 1
+Inserted line
 Line 2
 Line 3
```

### Multiple Hunks in Single File
```diff
--- a/file.txt
+++ b/file.txt
@@ -1,2 +1,2 @@
-First change
+First replacement
 Context
@@ -5,2 +5,2 @@
 More context
-Second change
+Second replacement
```

## Line Ending Handling

### Detection and Preservation
The patcher automatically detects the line ending style of each source file and preserves it in the output:

- **Windows files** (`\r\n`) → **Windows output** (`\r\n`)
- **Unix files** (`\n`) → **Unix output** (`\n`) 
- **Mac files** (`\r`) → **Mac output** (`\r`)
- **Mixed files** → **Dominant style** wins
- **Empty files** → **System default** (Windows: `\r\n`, Unix: `\n`)

### Cross-Platform Compatibility
The tool handles scenarios where patch and source files have different line endings:

| Scenario | Source File | Patch File | Output File |
|----------|-------------|------------|-------------|
| Windows dev, Unix patch | `\r\n` | `\n` | `\r\n` |
| Unix dev, Windows patch | `\n` | `\r\n` | `\n` |
| Mixed environment | `\r\n` | `\n` | `\r\n` |

## Output and Feedback

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

## Testing

### Comprehensive Test Suite
The included test suite (`run_unified_diff_patcher_TESTS.py`) validates:

- **16 comprehensive test cases** covering all edge cases
- **Line ending preservation** across different scenarios
- **Cross-platform compatibility** testing
- **Error condition handling**

### Running Tests
```bash
python run_unified_diff_patcher_TESTS.py
```

### Test Coverage
- ✅ Simple operations (add, delete, replace)
- ✅ Complex scenarios (multiple hunks, mixed operations)
- ✅ Edge cases (empty files, no newlines, single lines)
- ✅ Line ending variations (Windows, Unix, mixed)
- ✅ Cross-platform patches (Unix patch on Windows file)
- ✅ Whitespace handling (spaces, tabs)
- ✅ Large context hunks
- ✅ Error conditions (missing files, invalid patches)

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

## Examples of Supported Operations

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

## Troubleshooting

### Common Issues

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
```bash
python unified_diff_patcher.py problem.patch --verbose --dry-run
```

## Version History

### Current Version
- ✅ Complete unified diff support
- ✅ Intelligent line ending handling
- ✅ Comprehensive edge case support
- ✅ Cross-platform compatibility
- ✅ Extensive test coverage
- ✅ Production-ready reliability

## License

This tool is provided as-is for educational and practical use. Feel free to modify and distribute according to your needs.

## Contributing

To extend or improve this tool:
1. Add test cases to `run_unified_diff_patcher_TESTS.py`
2. Ensure all existing tests pass
3. Test edge cases thoroughly
4. Maintain cross-platform compatibility
5. Preserve line ending intelligence

---

**This unified diff patcher provides git-like patch functionality with enhanced line ending handling, making it ideal for Windows development environments while maintaining cross-platform compatibility.**
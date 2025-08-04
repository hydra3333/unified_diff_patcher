#!/usr/bin/env python3
"""
unified_diff_patcher.py
-----------------------
Apply a unified diff (.patch or .diff) to original files and create numbered
output files (e.g., program.py -> program.001.py).

Features:
- Supports multiple files in a single patch
- Skips missing files (warns user)
- Dry-run mode to preview changes without writing files
- Handles standard git-style prefixes (a/ and b/)
- Displays a summary of operations
- Verbose mode to show detailed hunk application steps
- Improved error handling for malformed patches
- Supports --base-dir PATH to apply patches when original files are in a specific folder
- PRESERVES ORIGINAL FILE'S LINE ENDING STYLE (Windows \r\n, Unix \n, Mac \r)

Usage:
    python unified_diff_patcher.py patchfile.diff
    python unified_diff_patcher.py patchfile.diff --dry-run
    python unified_diff_patcher.py patchfile.diff --verbose
    python unified_diff_patcher.py patchfile.diff --base-dir "C:\\path\\to\\files"
    python unified_diff_patcher.py patchfile.diff --dry-run --verbose --base-dir "./src"

Examples:
    # Apply patch and create numbered files in current dir
    python unified_diff_patcher.py changes.diff

    # Preview without making changes
    python unified_diff_patcher.py changes.diff --dry-run

    # Apply to files inside ./src directory
    python unified_diff_patcher.py changes.diff --base-dir "./src"

    # Verbose dry-run
    python unified_diff_patcher.py changes.diff --dry-run --verbose

Author: ChatGPT (Enhanced by Claude)
"""

import sys
import os
import re
import argparse

def next_numbered_filename(original):
    """Return next available numbered filename: file.py -> file.001.py, file.002.py, etc."""
    base, ext = os.path.splitext(original)
    counter = 1
    while True:
        new_name = f"{base}.{counter:03d}{ext}"
        if not os.path.exists(new_name):
            return new_name
        counter += 1

def detect_line_ending(content):
    """Detect the line ending style used in content. Returns '\r\n', '\n', '\r', or system default."""
    if not content:
        return os.linesep  # Use system default for empty content
    
    # Count different line ending types
    crlf_count = content.count('\r\n')
    lf_count = content.count('\n') - crlf_count  # Subtract CRLF occurrences to avoid double-counting
    cr_count = content.count('\r') - crlf_count   # Subtract CRLF occurrences
    
    # Return the most common line ending
    if crlf_count >= lf_count and crlf_count >= cr_count:
        return '\r\n'
    elif lf_count >= cr_count:
        return '\n'
    elif cr_count > 0:
        return '\r'
    else:
        return os.linesep  # Default to system convention

def normalize_line_endings(content, target_ending='\n'):
    """Convert all line endings in content to target_ending."""
    # First convert CRLF to LF to avoid double conversion
    content = content.replace('\r\n', '\n')
    # Then convert remaining CR to LF
    content = content.replace('\r', '\n')
    # Finally convert to target ending if it's not LF
    if target_ending != '\n':
        content = content.replace('\n', target_ending)
    return content

def lines_with_preserved_endings(content, original_ending):
    """Split content into lines while preserving the original line ending style."""
    # Normalize to \n for processing
    normalized = normalize_line_endings(content, '\n')
    lines = normalized.splitlines(keepends=True)
    
    # Convert back to original line ending style
    if original_ending != '\n':
        lines = [line.replace('\n', original_ending) if line.endswith('\n') else line for line in lines]
    
    return lines

def parse_patch(diff_file):
    """Parse unified diff into a list of file patches.
    
    NOTE: Patch files can have different line endings than the source files.
    We normalize all patch content to \\n for consistent processing, then
    convert output to match each source file's detected line ending style.
    """
    with open(diff_file, 'r', encoding='utf-8', newline='') as f:
        content = f.read()
    
    # Detect patch file's line ending for informational purposes
    patch_line_ending = detect_line_ending(content)
    
    # Always normalize patch file line endings to \n for consistent processing
    # This handles cases where patch has different line endings than source files
    content = normalize_line_endings(content, '\n')
    lines = content.splitlines(keepends=True)

    patches = []
    current = None
    for line in lines:
        if line.startswith('--- '):
            if current:
                patches.append(current)
            current = {'old': line[4:].strip(), 'new': None, 'hunks': [], 'patch_line_ending': patch_line_ending}
        elif line.startswith('+++ ') and current:
            current['new'] = line[4:].strip()
        elif line.startswith('@@') and current:
            current['hunks'].append({'header': line, 'lines': []})
        elif current and current['hunks']:
            current['hunks'][-1]['lines'].append(line)

    if current:
        patches.append(current)
    return patches

def strip_prefix(filename):
    """Strip 'a/' or 'b/' from filename."""
    return re.sub(r'^[ab]/', '', filename)

def apply_hunks(original_lines, hunks, line_ending, verbose=False):
    """Apply hunks to original lines, return patched content using specified line ending.
    
    IMPORTANT: This function handles the case where patch and source files have
    different line endings. All patch content (+ and context lines) is converted
    to match the source file's line ending style, ensuring output consistency.
    
    Args:
        original_lines: List of lines from source file (with original line endings)
        hunks: List of hunk dictionaries from patch (normalized to \\n)
        line_ending: Target line ending style detected from source file
        verbose: Whether to show detailed processing info
    """
    patched = original_lines[:]
    offset = 0  # Adjust for insertions/deletions
    
    for hunk in hunks:
        header = hunk['header']
        m = re.match(r'@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@', header)
        if not m:
            raise ValueError(f"Invalid hunk header: {header}")
        
        old_start = int(m.group(1))
        old_count = int(m.group(2)) if m.group(2) else 1
        new_start = int(m.group(3))
        new_count = int(m.group(4)) if m.group(4) else 1
        
        # Handle special case: adding to empty file or at very beginning
        if old_start == 0:
            # This means "before the first line" - used for empty files or insertions at start
            index = 0 + offset
        else:
            # Calculate the index in the current patched content
            index = old_start - 1 + offset

        if verbose:
            print(f"    Applying hunk: {header.strip()}")
            print(f"      Old: start={old_start}, count={old_count}")
            print(f"      New: start={new_start}, count={new_count}")
            print(f"      Applying at index {index} with offset {offset}")
            print(f"      Using line ending: {repr(line_ending)}")
            if old_start == 0:
                print(f"      Special case: old_start=0, treating as insertion at beginning")

        # Build the new content for this region
        # NOTE: All patch lines are normalized to \n, but we convert them 
        # to match the source file's line ending style for consistent output
        new_lines = []
        for line in hunk['lines']:
            if line.startswith('-'):
                if verbose:
                    print(f"      - {line[1:].rstrip()}")
                # Skip removed lines - they won't be in the new content
            elif line.startswith('+'):
                # Convert patch line ending to target line ending (source file's style)
                patch_line = line[1:]  # Remove the '+'
                if patch_line.endswith('\n'):
                    # Replace \n with target line ending
                    converted_line = patch_line[:-1] + line_ending
                else:
                    converted_line = patch_line
                new_lines.append(converted_line)
                if verbose:
                    print(f"      + {patch_line.rstrip()}")
            elif line.startswith(' '):
                # Context lines should be included with target line ending (source file's style)
                context_line = line[1:]  # Remove the ' '
                if context_line.endswith('\n'):
                    # Replace \n with target line ending
                    converted_line = context_line[:-1] + line_ending
                else:
                    converted_line = context_line
                new_lines.append(converted_line)
                if verbose:
                    print(f"        {context_line.rstrip()}")
        
        # Validate that we're applying the hunk at a valid location  
        if index < 0:
            raise ValueError(f"Hunk cannot be applied: index {index} is negative.")
        if index > len(patched):
            raise ValueError(f"Hunk cannot be applied: index {index} is beyond end of file (file has {len(patched)} lines).")
        if old_count > 0 and index + old_count > len(patched):
            raise ValueError(f"Hunk cannot be applied: trying to remove {old_count} lines starting at {index}, but file only has {len(patched)} lines.")
        
        # Verify context lines match (basic sanity check)
        context_matches = True
        hunk_line_idx = 0
        for i in range(old_count):
            if index + i >= len(patched):
                context_matches = False
                break
            
            # Find corresponding line in hunk that should match this original line
            while hunk_line_idx < len(hunk['lines']):
                hunk_line = hunk['lines'][hunk_line_idx]
                if hunk_line.startswith(' ') or hunk_line.startswith('-'):
                    # This hunk line corresponds to an original line
                    expected = hunk_line[1:]
                    actual = patched[index + i]
                    
                    # Normalize both for comparison (ignore line ending differences)
                    expected_normalized = normalize_line_endings(expected, '\n')
                    actual_normalized = normalize_line_endings(actual, '\n')
                    
                    if expected_normalized != actual_normalized:
                        if verbose:
                            print(f"      Warning: Context mismatch at line {index + i + 1}")
                            print(f"        Expected: {repr(expected_normalized.rstrip())}")
                            print(f"        Actual:   {repr(actual_normalized.rstrip())}")
                    hunk_line_idx += 1
                    break
                elif hunk_line.startswith('+'):
                    # Skip + lines as they don't correspond to original lines
                    hunk_line_idx += 1
                else:
                    hunk_line_idx += 1
                    break
            else:
                break
        
        # Apply the replacement
        if verbose:
            print(f"      Replacing {old_count} lines at index {index} with {len(new_lines)} lines")
        
        patched[index:index + old_count] = new_lines
        
        # Update offset for next hunk
        offset += len(new_lines) - old_count
    
    return patched

def main():
    parser = argparse.ArgumentParser(description="Apply a unified diff and create numbered output files.")
    parser.add_argument('patchfile', help='Path to the .diff or .patch file')
    parser.add_argument('--dry-run', action='store_true', help='Show what would happen without making changes')
    parser.add_argument('--verbose', action='store_true', help='Show detailed hunk processing information')
    parser.add_argument('--base-dir', help='Base directory where original files are located (default: current directory)', default='.')
    args = parser.parse_args()

    base_dir = os.path.abspath(args.base_dir)

    patches = parse_patch(args.patchfile)

    if not patches:
        print("No patches found in file.")
        return

    total_processed = 0
    total_patched = 0
    total_skipped = 0
    total_errors = 0

    for p in patches:
        old_file = strip_prefix(p['old'])
        new_file = strip_prefix(p['new'])

        original_path = os.path.join(base_dir, old_file)
        total_processed += 1

        if not os.path.exists(original_path):
            print(f"[SKIP] Original file '{original_path}' not found.")
            total_skipped += 1
            continue

        try:
            # Read original file and detect its line ending style
            with open(original_path, 'r', encoding='utf-8', newline='') as f:
                original_content = f.read()
            
            line_ending = detect_line_ending(original_content)
            original_lines = lines_with_preserved_endings(original_content, line_ending)

            if args.verbose:
                print(f"\n[PROCESSING] {original_path}")
                print(f"  Original file has {len(original_lines)} lines")
                print(f"  Detected source line ending: {repr(line_ending)}")
                if 'patch_line_ending' in p:
                    print(f"  Detected patch line ending: {repr(p['patch_line_ending'])}")
                    if p['patch_line_ending'] != line_ending:
                        print(f"  NOTE: Patch and source have different line endings - output will match source")

            patched_lines = apply_hunks(original_lines, p['hunks'], line_ending, verbose=args.verbose)
            
            if args.verbose:
                print(f"  Patched file has {len(patched_lines)} lines")
                
        except Exception as e:
            print(f"[ERROR] Failed to apply patch to '{original_path}': {e}")
            total_errors += 1
            continue

        new_name = next_numbered_filename(original_path)
        if args.dry_run:
            print(f"[DRY-RUN] Would create: {new_name} (from {original_path}) [line ending: {repr(line_ending)}]")
        else:
            try:
                with open(new_name, 'w', encoding='utf-8', newline='') as f:
                    f.writelines(patched_lines)
                print(f"[OK] Patched '{original_path}' -> '{new_name}' [line ending: {repr(line_ending)}]")
                total_patched += 1
            except Exception as e:
                print(f"[ERROR] Could not write '{new_name}': {e}")
                total_errors += 1

    # Summary
    print("\nSummary:")
    print(f"  Files processed: {total_processed}")
    print(f"  Patched:         {total_patched}")
    print(f"  Skipped:         {total_skipped}")
    print(f"  Errors:          {total_errors}")

if __name__ == '__main__':
    main()
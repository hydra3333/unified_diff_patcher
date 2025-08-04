#!/usr/bin/env python3
"""
run_patch_tests.py
-------------------
This script creates a test environment for unified_diff_patcher.py and verifies
that the patch application logic works correctly.

Steps:
1. Creates a subfolder "patch_test_env" in the current directory.
2. Generates sample original files and unified diff patches.
3. Runs unified_diff_patcher.py with:
    - Dry-run mode (optional)
    - Normal mode (optional) 
    - Both modes (default)
4. Verifies the generated numbered files against expected content (if normal mode run).
5. Prints detailed results and a summary.

Usage:
    python run_patch_tests.py                    # Run both dry-run and normal modes
    python run_patch_tests.py --dry-run-only     # Only run dry-run tests
    python run_patch_tests.py --normal-only      # Only run normal mode tests  
    python run_patch_tests.py --verbose          # Run patcher in verbose mode

Prerequisites:
- Python 3
- unified_diff_patcher.py must be in the same directory as this script.

Author: ChatGPT (Enhanced by Claude)
"""

import os
import subprocess
import sys

BASE_DIR = os.getcwd()
TEST_DIR = os.path.join(BASE_DIR, "patch_test_env")
PATCHER_SCRIPT = os.path.join(BASE_DIR, "unified_diff_patcher.py")

# Test files and expected behavior - now with explicit line ending handling
TESTS = [
    {
        "name": "Simple Add Line (Windows CRLF)",
        "source": "file1.txt",
        "content": "Line 1\r\nLine 2\r\nLine 3\r\n",  # Windows line endings
        "patch": """--- a/file1.txt
+++ b/file1.txt
@@ -1,3 +1,4 @@
 Line 1
 Line 2
 Line 3
+Line 4
""",
        "expected": "Line 1\r\nLine 2\r\nLine 3\r\nLine 4\r\n"  # Should preserve Windows endings
    },
    {
        "name": "Replace Middle Line (Unix LF)",
        "source": "file2.txt", 
        "content": "Alpha\nBeta\nGamma\n",  # Unix line endings
        "patch": """--- a/file2.txt
+++ b/file2.txt
@@ -1,3 +1,3 @@
 Alpha
-Beta
+Delta
 Gamma
""",
        "expected": "Alpha\nDelta\nGamma\n"  # Should preserve Unix endings
    },
    {
        "name": "Delete a Line (Windows CRLF)",
        "source": "file3.txt",
        "content": "One\r\nTwo\r\nThree\r\nFour\r\n",  # Windows line endings
        "patch": """--- a/file3.txt
+++ b/file3.txt
@@ -2,3 +2,2 @@
 Two
-Three
 Four
""",
        "expected": "One\r\nTwo\r\nFour\r\n"  # Should preserve Windows endings
    },
    {
        "name": "Add Line at Beginning",
        "source": "file4.txt", 
        "content": "Second\nThird\nFourth\n",
        "patch": """--- a/file4.txt
+++ b/file4.txt
@@ -1,3 +1,4 @@
+First
 Second
 Third
 Fourth
""",
        "expected": "First\nSecond\nThird\nFourth\n"
    },
    {
        "name": "Add Multiple Lines in Middle",
        "source": "file5.txt",
        "content": "Start\nEnd\n",
        "patch": """--- a/file5.txt
+++ b/file5.txt
@@ -1,2 +1,4 @@
 Start
+Middle1
+Middle2
 End
""",
        "expected": "Start\nMiddle1\nMiddle2\nEnd\n"
    },
    {
        "name": "Multiple Hunks Same File (Unix LF)",
        "source": "file6.txt",
        "content": "A\nB\nC\nD\nE\nF\n",  # Unix line endings
        "patch": """--- a/file6.txt
+++ b/file6.txt
@@ -1,2 +1,2 @@
-A
+AA
 B
@@ -5,2 +5,2 @@
 E
-F
+FF
""",
        "expected": "AA\nB\nC\nD\nE\nFF\n"  # Should preserve Unix endings
    },
    {
        "name": "Delete First Line",
        "source": "file7.txt",
        "content": "Remove\nKeep1\nKeep2\n",
        "patch": """--- a/file7.txt
+++ b/file7.txt
@@ -1,3 +1,2 @@
-Remove
 Keep1
 Keep2
""",
        "expected": "Keep1\nKeep2\n"
    },
    {
        "name": "Delete Last Line", 
        "source": "file8.txt",
        "content": "Keep1\nKeep2\nRemove\n",
        "patch": """--- a/file8.txt
+++ b/file8.txt
@@ -1,3 +1,2 @@
 Keep1
 Keep2
-Remove
""",
        "expected": "Keep1\nKeep2\n"
    },
    {
        "name": "Single Line File Replacement",
        "source": "file9.txt",
        "content": "Original\n",
        "patch": """--- a/file9.txt
+++ b/file9.txt
@@ -1 +1 @@
-Original
+Replaced
""",
        "expected": "Replaced\n"
    },
    {
        "name": "Empty File to Content",
        "source": "file10.txt",
        "content": "",
        "patch": """--- a/file10.txt
+++ b/file10.txt
@@ -0,0 +1,2 @@
+First line
+Second line
""",
        "expected": "First line\r\nSecond line\r\n"  # Should use system default (Windows CRLF)
    },
    {
        "name": "Content to Empty File",
        "source": "file11.txt", 
        "content": "Delete me\nDelete me too\n",
        "patch": """--- a/file11.txt
+++ b/file11.txt
@@ -1,2 +0,0 @@
-Delete me
-Delete me too
""",
        "expected": ""
    },
    {
        "name": "No Newline at EOF (Original)",
        "source": "file12.txt",
        "content": "Line1\nLine2",  # No trailing newline
        "patch": """--- a/file12.txt
+++ b/file12.txt
@@ -1,2 +1,3 @@
 Line1
 Line2
+Line3
""",
        "expected": "Line1\nLine2\nLine3\n"
    },
    {
        "name": "Complex Mixed Operations",
        "source": "file13.txt",
        "content": "Keep1\nReplace1\nDelete1\nDelete2\nKeep2\nReplace2\nKeep3\n",
        "patch": """--- a/file13.txt
+++ b/file13.txt
@@ -1,7 +1,6 @@
 Keep1
-Replace1
-Delete1
-Delete2
+NewReplace1
+AddedLine
 Keep2
-Replace2
+NewReplace2
 Keep3
""",
        "expected": "Keep1\nNewReplace1\nAddedLine\nKeep2\nNewReplace2\nKeep3\n"
    },
    {
        "name": "Whitespace Only Changes",
        "source": "file14.txt",
        "content": "Line with spaces   \nLine with tabs\t\t\nNormal line\n",
        "patch": """--- a/file14.txt
+++ b/file14.txt
@@ -1,3 +1,3 @@
-Line with spaces   
+Line with spaces
-Line with tabs\t\t
+Line with tabs\t
 Normal line
""",
        "expected": "Line with spaces\nLine with tabs\t\nNormal line\n"
    },
    {
        "name": "Large Context Hunk",
        "source": "file15.txt",
        "content": "Context1\nContext2\nContext3\nOldLine\nContext4\nContext5\nContext6\n",
        "patch": """--- a/file15.txt
+++ b/file15.txt
@@ -1,7 +1,7 @@
 Context1
 Context2
 Context3
-OldLine
+NewLine
 Context4
 Context5
 Context6
""",
        "expected": "Context1\nContext2\nContext3\nNewLine\nContext4\nContext5\nContext6\n"
    },
    {
        "name": "Mixed Line Endings (CRLF dominant)",
        "source": "file16.txt",
        "content": "Line1\r\nLine2\nLine3\r\nLine4\r\n",  # Mixed, but mostly CRLF
        "patch": """--- a/file16.txt
+++ b/file16.txt
@@ -2,3 +2,3 @@
 Line2
-Line3
+ReplacedLine3
 Line4
""",
        "expected": "Line1\r\nLine2\r\nReplacedLine3\r\nLine4\r\n"  # Should use dominant CRLF style
    }
]

# Special test case for cross-line-ending scenario (handled separately)
CROSS_LINE_ENDING_TEST = {
    "name": "Cross Line Ending Test (Windows source, Unix patch)",
    "source": "file17.txt",
    "content": "WindowsLine1\r\nWindowsLine2\r\nWindowsLine3\r\n",  # Windows source
    "expected": "WindowsLine1\r\nWindowsLine2\r\nUnixPatchAddition\r\nWindowsLine3\r\n"  # Output should be Windows \r\n
}

def create_test_env():
    if os.path.exists(TEST_DIR):
        print(f"Removing old test directory: {TEST_DIR}")
        for root, dirs, files in os.walk(TEST_DIR, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(TEST_DIR)

    os.makedirs(TEST_DIR)
    print(f"Created test environment at {TEST_DIR}")

    # Create source files and patch file
    for t in TESTS:
        src_path = os.path.join(TEST_DIR, t["source"])
        with open(src_path, "w", encoding="utf-8", newline='') as f:
            f.write(t["content"])
    
    # Create the cross-line-ending test source file
    cross_src_path = os.path.join(TEST_DIR, CROSS_LINE_ENDING_TEST["source"])
    with open(cross_src_path, "w", encoding="utf-8", newline='') as f:
        f.write(CROSS_LINE_ENDING_TEST["content"])

    # Write patch file combining all patches  
    patch_path = os.path.join(TEST_DIR, "combined.patch")
    with open(patch_path, "w", encoding="utf-8", newline='') as f:
        for t in TESTS:
            f.write(t["patch"])
            f.write("\n")
    
    # Create a special cross-line-ending test patch with explicit Unix line endings
    cross_patch_path = os.path.join(TEST_DIR, "cross_line_ending.patch")
    cross_patch_content = """--- a/file17.txt
+++ b/file17.txt
@@ -1,3 +1,4 @@
 WindowsLine1
 WindowsLine2
+UnixPatchAddition
 WindowsLine3
"""
    # Ensure this patch file has Unix line endings regardless of system
    cross_patch_unix = cross_patch_content.replace('\r\n', '\n').replace('\r', '\n')
    with open(cross_patch_path, "w", encoding="utf-8", newline='') as f:
        f.write(cross_patch_unix)
    
    return patch_path, cross_patch_path

def run_patcher_dry_run(patch_path, verbose=False):
    print("\nRunning patcher (dry-run mode)...")
    cmd = [sys.executable, PATCHER_SCRIPT, patch_path, "--base-dir", TEST_DIR, "--dry-run"]
    if verbose:
        cmd.append("--verbose")
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    print("Dry-run output:")
    print(result.stdout)
    if result.stderr:
        print("Dry-run stderr:")
        print(result.stderr)

def run_patcher(patch_path, verbose=False):
    print("\nRunning patcher (normal mode)...")
    cmd = [sys.executable, PATCHER_SCRIPT, patch_path, "--base-dir", TEST_DIR]
    if verbose:
        cmd.append("--verbose")
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    print("Patcher output:")
    print(result.stdout)
    if result.stderr:
        print("Patcher stderr:")
        print(result.stderr)
    return result.returncode

def verify_cross_line_ending_test(test_info):
    """Verify the cross-line-ending test specifically and show detailed analysis."""
    base = os.path.join(TEST_DIR, test_info["source"])
    candidate = None
    for i in range(1, 50):
        name = f"{os.path.splitext(base)[0]}.{i:03d}{os.path.splitext(base)[1]}"
        if os.path.exists(name):
            candidate = name
            break
    
    if not candidate:
        print(f"  FAIL: No output file found for {test_info['source']}")
        return
    
    with open(candidate, "r", encoding="utf-8", newline='') as f:
        actual = f.read()
    
    def analyze_endings(s, name):
        crlf = s.count('\r\n')
        lf = s.count('\n') - crlf
        cr = s.count('\r') - crlf
        print(f"  {name}: CRLF={crlf}, LF={lf}, CR={cr}")
        if crlf > 0:
            return "Windows (\\r\\n)"
        elif lf > 0:
            return "Unix (\\n)"
        elif cr > 0:
            return "Mac (\\r)"
        else:
            return "No line endings"
    
    print(f"  Source file: {test_info['source']}")
    with open(os.path.join(TEST_DIR, test_info["source"]), "r", encoding="utf-8", newline='') as f:
        source_content = f.read()
    source_style = analyze_endings(source_content, "Source")
    
    print(f"  Output file: {candidate}")
    output_style = analyze_endings(actual, "Output")
    
    expected_style = analyze_endings(test_info["expected"], "Expected")
    
    if actual == test_info["expected"]:
        print(f"  PASS: Output matches expected content exactly")
        print(f"  SUCCESS: Line ending preservation worked - {source_style} → {output_style}")
    else:
        print(f"  FAIL: Content mismatch")
        print(f"  Expected: {repr(test_info['expected'][:50])}...")
        print(f"  Actual:   {repr(actual[:50])}...")

def verify_results():
    print("\nVerifying results...")
    results = []
    for t in TESTS:
        base = os.path.join(TEST_DIR, t["source"])
        candidate = None
        for i in range(1, 50):  # search for numbered output
            name = f"{os.path.splitext(base)[0]}.{i:03d}{os.path.splitext(base)[1]}"
            if os.path.exists(name):
                candidate = name
                break
        
        if candidate:
            with open(candidate, "r", encoding="utf-8", newline='') as f:
                actual = f.read()
            
            # For line-ending aware patcher, we expect EXACT matches (no normalization)
            if actual == t["expected"]:
                results.append((t["name"], True, None))
            else:
                # Show the difference for debugging, including line ending details
                diff_info = f"Expected {len(t['expected'])} chars, got {len(actual)} chars"
                if len(t['expected']) <= 200 and len(actual) <= 200:
                    diff_info += f"\nExpected: {repr(t['expected'])}\nActual:   {repr(actual)}"
                
                # Also show line ending analysis
                def analyze_endings(s):
                    crlf = s.count('\r\n')
                    lf = s.count('\n') - crlf
                    cr = s.count('\r') - crlf
                    return f"CRLF:{crlf}, LF:{lf}, CR:{cr}"
                
                diff_info += f"\nExpected endings: {analyze_endings(t['expected'])}"
                diff_info += f"\nActual endings: {analyze_endings(actual)}"
                results.append((t["name"], False, diff_info))
        else:
            results.append((t["name"], False, f"No output file found for {t['source']}"))

    print("\nTest Results:")
    passed = 0
    for name, ok, info in results:
        status = 'PASS' if ok else 'FAIL'
        print(f"  {name}: {status}")
        if not ok and info:
            print(f"    {info}")
        if ok:
            passed += 1
    
    print(f"\nSummary: {passed}/{len(results)} tests passed.")
    return passed == len(results)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Test unified_diff_patcher.py with comprehensive test cases.")
    parser.add_argument('--dry-run-only', action='store_true', help='Only run dry-run tests, do not create output files')
    parser.add_argument('--normal-only', action='store_true', help='Only run normal mode tests, skip dry-run')
    parser.add_argument('--verbose', action='store_true', help='Run patcher in verbose mode')
    args = parser.parse_args()
    
    if args.dry_run_only and args.normal_only:
        print("ERROR: Cannot specify both --dry-run-only and --normal-only")
        return
    
    if not os.path.exists(PATCHER_SCRIPT):
        print("ERROR: unified_diff_patcher.py not found in current directory.")
        return

    patch_path, cross_patch_path = create_test_env()
    
    # Determine what modes to run
    run_dry_run = not args.normal_only  # Default True unless --normal-only
    run_normal = not args.dry_run_only  # Default True unless --dry-run-only
    
    print(f"\nTest Mode: {'Dry-run only' if args.dry_run_only else 'Normal only' if args.normal_only else 'Both dry-run and normal'}")
    
    # Run main test suite
    if run_dry_run:
        run_patcher_dry_run(patch_path, verbose=args.verbose)
    
    returncode = 0
    if run_normal:
        returncode = run_patcher(patch_path, verbose=args.verbose)
        if returncode != 0:
            print(f"WARNING: Patcher returned non-zero exit code: {returncode}")
    
    # Run cross-line-ending test separately
    print("\n" + "="*60)
    print("CROSS-LINE-ENDING TEST")
    print("="*60)
    print("Testing: Windows source file + Unix patch file → Windows output")
    
    if run_dry_run:
        run_patcher_dry_run(cross_patch_path, verbose=args.verbose)
    
    cross_returncode = 0
    if run_normal:
        cross_returncode = run_patcher(cross_patch_path, verbose=args.verbose)
    
    # Only verify results if we ran normal mode (created output files)
    if run_normal:
        all_passed = verify_results()
        print("\nOverall Result:", "SUCCESS" if all_passed else "FAILURE")
        
        # Verify the cross-line-ending test specifically
        print(f"\nCross-line-ending test verification:")
        verify_cross_line_ending_test(CROSS_LINE_ENDING_TEST)
    else:
        print("\nDry-run completed. No output files created for verification.")

if __name__ == "__main__":
    main()
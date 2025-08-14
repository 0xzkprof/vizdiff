#!/usr/bin/env python3
"""
Side-by-Side File Comparison Tool
Compares two files line by line and displays differences highlighted in color.
"""

import argparse
import sys
import difflib
from typing import List, Tuple

# ANSI color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
    # Background colors for highlighting differences
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'

def read_file_lines(filename: str) -> List[str]:
    """Read all lines from a file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"Error: Could not decode '{filename}' as UTF-8.")
        sys.exit(1)

def highlight_char_differences(line1: str, line2: str) -> Tuple[str, str]:
    """Highlight blocks of characters that were changed between two lines."""
    # Use SequenceMatcher to find character-level differences
    matcher = difflib.SequenceMatcher(None, line1, line2)
    
    result1 = []
    result2 = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            result1.append(line1[i1:i2])
            result2.append(line2[j1:j2])
        elif tag == 'delete':
            # Only highlight if it's part of a replacement, not a pure deletion
            result1.append(line1[i1:i2])
            result2.append("")
        elif tag == 'insert':
            # Only highlight if it's part of a replacement, not a pure insertion
            result1.append("")
            result2.append(line2[j1:j2])
        elif tag == 'replace':
            # This is what we want to highlight - changed blocks
            result1.append(f"{Colors.BG_YELLOW}{Colors.BLACK}{line1[i1:i2]}{Colors.END}")
            result2.append(f"{Colors.BG_YELLOW}{Colors.BLACK}{line2[j1:j2]}{Colors.END}")
    
    return ''.join(result1), ''.join(result2)

def wrap_line(line: str, width: int) -> List[str]:
    """Wrap a line to fit within specified width, preserving ANSI color codes."""
    if not line:
        return ['']
    
    # For lines with ANSI codes, we need to be more careful about wrapping
    # This is a simplified approach - we'll wrap based on visible characters
    wrapped_lines = []
    current_line = ""
    visible_length = 0
    i = 0
    
    while i < len(line):
        if line[i:i+1] == '\033':  # ANSI escape sequence start
            # Find the end of the ANSI sequence
            end = i + 1
            while end < len(line) and line[end] not in ['m', 'H', 'J', 'K']:
                end += 1
            if end < len(line):
                end += 1
            # Add the entire ANSI sequence without counting its length
            current_line += line[i:end]
            i = end
        else:
            if visible_length >= width:
                wrapped_lines.append(current_line)
                current_line = ""
                visible_length = 0
            current_line += line[i]
            visible_length += 1
            i += 1
    
    if current_line or not wrapped_lines:
        wrapped_lines.append(current_line)
    
    return wrapped_lines

def compare_files(file1_path: str, file2_path: str, width: int = 120, no_color: bool = False):
    """Compare two files and display side by side with highlighted differences."""
    
    # Read files
    lines1 = read_file_lines(file1_path)
    lines2 = read_file_lines(file2_path)
    
    # Pad shorter file with empty lines
    max_lines = max(len(lines1), len(lines2))
    lines1 += [''] * (max_lines - len(lines1))
    lines2 += [''] * (max_lines - len(lines2))
    
    # Calculate column width (leave space for line numbers and separator)
    col_width = (width - 7) // 2  # 7 chars for line numbers, marker, and separator
    
    # Print header
    header1 = f"{Colors.BOLD}{file1_path}{Colors.END}" if not no_color else file1_path
    header2 = f"{Colors.BOLD}{file2_path}{Colors.END}" if not no_color else file2_path
    
    print("=" * width)
    print(f"{'':>5} {header1:<{col_width}} | {header2}")
    print("=" * width)
    
    # Compare and display lines
    diff_count = 0
    for i, (line1, line2) in enumerate(zip(lines1, lines2), 1):
        line1 = line1.rstrip('\n\r')
        line2 = line2.rstrip('\n\r')
        
        # Check if lines are different
        if line1 != line2:
            diff_count += 1
            
            if not no_color:
                # Highlight character-level differences
                highlighted1, highlighted2 = highlight_char_differences(line1, line2)
                line_num_color = Colors.YELLOW
                marker = f"{Colors.RED}*{Colors.END}"
            else:
                highlighted1, highlighted2 = line1, line2
                line_num_color = ""
                marker = "*"
            
            # Wrap lines if they're too long
            wrapped1 = wrap_line(highlighted1, col_width)
            wrapped2 = wrap_line(highlighted2, col_width)
            
            # Make both wrapped lists the same length
            max_wrapped = max(len(wrapped1), len(wrapped2))
            wrapped1 += [''] * (max_wrapped - len(wrapped1))
            wrapped2 += [''] * (max_wrapped - len(wrapped2))
            
            # Print all wrapped lines
            for j, (w1, w2) in enumerate(zip(wrapped1, wrapped2)):
                if j == 0:  # First line gets the line number and marker
                    line_num = f"{line_num_color}{i:4d}{Colors.END if not no_color else ''}"
                    print(f"{line_num}{marker} {w1:<{col_width}} | {w2}")
                else:  # Continuation lines get spaces
                    print(f"{'':>5} {w1:<{col_width}} | {w2}")
        else:
            # Lines are identical
            wrapped = wrap_line(line1, col_width)
            
            # Print all wrapped lines
            for j, w_line in enumerate(wrapped):
                if j == 0:  # First line gets the line number
                    line_num = f"{i:4d} "
                    print(f"{line_num} {w_line:<{col_width}} | {w_line}")
                else:  # Continuation lines
                    print(f"{'':>5} {w_line:<{col_width}} | {w_line}")
    
    # Print summary
    print("=" * width)
    summary_color = Colors.GREEN if diff_count == 0 else Colors.YELLOW
    summary = f"Comparison complete: {diff_count} differing lines out of {max_lines} total lines"
    
    if not no_color:
        print(f"{summary_color}{summary}{Colors.END}")
    else:
        print(summary)
    
    if diff_count > 0 and not no_color:
        print(f"\nLegend:")
        print(f"  {Colors.BG_YELLOW}{Colors.BLACK}Yellow background{Colors.END}: Changed blocks of characters")
        print(f"  {Colors.RED}*{Colors.END}: Line number marker for differing lines")
        print(f"  Continuation lines are indented without line numbers")

def main():
    parser = argparse.ArgumentParser(
        description="Compare two files side by side with highlighted differences",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python file_diff.py file1.txt file2.txt
  python file_diff.py config.old config.new --width 120
  python file_diff.py log1.txt log2.txt --no-color
        """
    )
    
    parser.add_argument('file1', help='First file to compare')
    parser.add_argument('file2', help='Second file to compare')
    parser.add_argument('-w', '--width', type=int, default=120, 
                       help='Display width in characters (default: 120)')
    parser.add_argument('--no-color', action='store_true',
                       help='Disable colored output')
    
    args = parser.parse_args()
    
    # Validate width
    if args.width < 40:
        print("Error: Width must be at least 40 characters.")
        sys.exit(1)
    
    compare_files(args.file1, args.file2, args.width, args.no_color)

if __name__ == "__main__":
    main()

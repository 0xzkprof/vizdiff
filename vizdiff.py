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
    """Highlight character-level differences between two lines."""
    # Use SequenceMatcher to find character-level differences
    matcher = difflib.SequenceMatcher(None, line1, line2)
    
    result1 = []
    result2 = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            result1.append(line1[i1:i2])
            result2.append(line2[j1:j2])
        elif tag == 'delete':
            result1.append(f"{Colors.BG_RED}{line1[i1:i2]}{Colors.END}")
            result2.append("")
        elif tag == 'insert':
            result1.append("")
            result2.append(f"{Colors.BG_GREEN}{line2[j1:j2]}{Colors.END}")
        elif tag == 'replace':
            result1.append(f"{Colors.BG_RED}{line1[i1:i2]}{Colors.END}")
            result2.append(f"{Colors.BG_GREEN}{line2[j1:j2]}{Colors.END}")
    
    return ''.join(result1), ''.join(result2)

def truncate_line(line: str, max_width: int) -> str:
    """Truncate line if it's too long, preserving color codes."""
    # Simple truncation - could be improved to handle ANSI codes better
    if len(line) > max_width:
        return line[:max_width-3] + "..."
    return line

def compare_files(file1_path: str, file2_path: str, width: int = 80, no_color: bool = False):
    """Compare two files and display side by side with highlighted differences."""
    
    # Read files
    lines1 = read_file_lines(file1_path)
    lines2 = read_file_lines(file2_path)
    
    # Pad shorter file with empty lines
    max_lines = max(len(lines1), len(lines2))
    lines1 += [''] * (max_lines - len(lines1))
    lines2 += [''] * (max_lines - len(lines2))
    
    # Calculate column width
    col_width = (width - 5) // 2  # 5 chars for separator and line numbers
    
    # Print header
    header1 = f"{Colors.BOLD}{file1_path}{Colors.END}" if not no_color else file1_path
    header2 = f"{Colors.BOLD}{file2_path}{Colors.END}" if not no_color else file2_path
    
    print("=" * width)
    print(f"{header1:<{col_width}} | {header2}")
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
                
                # Line number with color
                line_num = f"{Colors.YELLOW}{i:4d}{Colors.END}"
            else:
                highlighted1, highlighted2 = line1, line2
                line_num = f"{i:4d}"
            
            # Truncate if necessary
            display1 = truncate_line(highlighted1, col_width)
            display2 = truncate_line(highlighted2, col_width)
            
            # Print with difference marker
            marker = f"{Colors.RED}*{Colors.END}" if not no_color else "*"
            print(f"{line_num}{marker} {display1:<{col_width}} | {display2}")
        else:
            # Lines are identical
            display_line = truncate_line(line1, col_width)
            line_num = f"{i:4d} "
            print(f"{line_num} {display_line:<{col_width}} | {display_line}")
    
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
        print(f"  {Colors.BG_RED}Red background{Colors.END}: Content removed/changed in left file")
        print(f"  {Colors.BG_GREEN}Green background{Colors.END}: Content added/changed in right file")
        print(f"  {Colors.RED}*{Colors.END}: Line number marker for differing lines")

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

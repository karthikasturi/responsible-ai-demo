#!/usr/bin/env python3
"""
Update Requirements Script
Updates package versions in requirements.txt to latest available on PyPI
"""

import re
import sys
import json
import urllib.request
import urllib.error
from typing import Dict, Optional, Tuple


def get_latest_version(package_name: str) -> Optional[str]:
    """
    Fetch the latest version of a package from PyPI.
    
    Args:
        package_name: Name of the package
        
    Returns:
        Latest version string or None if not found
    """
    url = f"https://pypi.org/pypi/{package_name}/json"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data['info']['version']
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"⚠️  Package '{package_name}' not found on PyPI", file=sys.stderr)
        else:
            print(f"⚠️  HTTP Error {e.code} for package '{package_name}'", file=sys.stderr)
        return None
    except urllib.error.URLError as e:
        print(f"⚠️  Network error for package '{package_name}': {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"⚠️  Error fetching '{package_name}': {e}", file=sys.stderr)
        return None


def parse_requirement_line(line: str) -> Tuple[Optional[str], Optional[str], str]:
    """
    Parse a requirements.txt line.
    
    Args:
        line: A line from requirements.txt
        
    Returns:
        Tuple of (package_name, current_version, original_line)
    """
    line = line.strip()
    
    # Skip empty lines and comments
    if not line or line.startswith('#'):
        return None, None, line
    
    # Match patterns like: package==1.2.3, package>=1.2.3, package~=1.2.3, package
    match = re.match(r'^([a-zA-Z0-9\-_\.]+)(==|>=|<=|~=|>|<)?(.+)?', line)
    
    if match:
        package_name = match.group(1)
        operator = match.group(2) if match.group(2) else None
        version = match.group(3).strip() if match.group(3) else None
        return package_name, version, line
    
    return None, None, line


def update_requirements(
    input_file: str = 'requirements.txt',
    output_file: str = 'requirements.txt',
    dry_run: bool = False
) -> None:
    """
    Update requirements.txt with latest versions from PyPI.
    
    Args:
        input_file: Path to input requirements.txt
        output_file: Path to output requirements.txt
        dry_run: If True, only show what would change without writing
    """
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"❌ Error: {input_file} not found", file=sys.stderr)
        sys.exit(1)
    
    updated_lines = []
    changes: Dict[str, Tuple[str, str]] = {}
    
    print(f"🔍 Checking {len(lines)} packages for updates...")
    print("-" * 60)
    
    for line in lines:
        package_name, current_version, original_line = parse_requirement_line(line)
        
        # Keep comments and empty lines as-is
        if package_name is None:
            updated_lines.append(original_line + '\n' if not original_line.endswith('\n') else original_line)
            continue
        
        # Fetch latest version
        latest_version = get_latest_version(package_name)
        
        if latest_version:
            if current_version and current_version != latest_version:
                print(f"📦 {package_name}: {current_version} → {latest_version}")
                changes[package_name] = (current_version, latest_version)
                updated_lines.append(f"{package_name}=={latest_version}\n")
            elif not current_version:
                print(f"📦 {package_name}: (no version) → {latest_version}")
                changes[package_name] = ("(no version)", latest_version)
                updated_lines.append(f"{package_name}=={latest_version}\n")
            else:
                print(f"✓  {package_name}: {current_version} (up to date)")
                updated_lines.append(original_line + '\n' if not original_line.endswith('\n') else original_line)
        else:
            print(f"⚠️  {package_name}: Unable to fetch version, keeping original")
            updated_lines.append(original_line + '\n' if not original_line.endswith('\n') else original_line)
    
    print("-" * 60)
    print(f"\n📊 Summary: {len(changes)} package(s) updated")
    
    if changes:
        print("\nChanges:")
        for pkg, (old, new) in changes.items():
            print(f"  • {pkg}: {old} → {new}")
    
    # Write output
    if dry_run:
        print(f"\n🔍 Dry run - no changes written to {output_file}")
        print("\nTo apply changes, run without --dry-run flag")
    else:
        with open(output_file, 'w') as f:
            f.writelines(updated_lines)
        print(f"\n✅ Updated {output_file}")
        print("\n⚠️  Remember to test your application after updating!")
        print("   Run: pip install -r requirements.txt")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Update requirements.txt with latest PyPI versions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Update requirements.txt
  python update_requirements.py
  
  # Dry run to see what would change
  python update_requirements.py --dry-run
  
  # Update specific file
  python update_requirements.py -i requirements.txt -o requirements-new.txt
  
  # Check for updates without applying
  python update_requirements.py --dry-run
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        default='requirements.txt',
        help='Input requirements file (default: requirements.txt)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='requirements.txt',
        help='Output requirements file (default: requirements.txt)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would change without writing files'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📦 PyPI Requirements Updater")
    print("=" * 60)
    print()
    
    update_requirements(
        input_file=args.input,
        output_file=args.output,
        dry_run=args.dry_run
    )


if __name__ == '__main__':
    main()

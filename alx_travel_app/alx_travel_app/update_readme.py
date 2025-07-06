#!/usr/bin/env python3
"""
Script to update the root README.md with content from alx_travel_app/README.md
"""

import os
import shutil
from pathlib import Path

def update_readme():
    """Update root README.md with content from alx_travel_app/README.md"""
    
    # Define paths
    root_dir = Path(__file__).parent
    source_readme = root_dir / "alx_travel_app" / "README.md"
    target_readme = root_dir / "README.md"
    
    # Check if source file exists
    if not source_readme.exists():
        print(f"Error: Source file {source_readme} does not exist")
        return False
    
    try:
        # Copy the content
        shutil.copy2(source_readme, target_readme)
        print(f"Successfully updated {target_readme} with content from {source_readme}")
        return True
    except Exception as e:
        print(f"Error updating README: {e}")
        return False

if __name__ == "__main__":
    update_readme() 
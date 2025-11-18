"""
Script to split the Internal Support vector store into smaller chunks under 10MB.
"""

import json
import os
from pathlib import Path

def split_internal_support():
    """Split Internal Support articles into smaller chunks."""

    print("🔍 Splitting Internal Support articles...")

    # Load the large Internal Support file
    with open("vector_stores/Internal_Support_vector_store.json", "r", encoding="utf-8") as f:
        articles = json.load(f)

    print(f"✅ Loaded {len(articles)} Internal Support articles")

    # Split into chunks of ~400 articles each (should be under 10MB)
    chunk_size = 400
    chunks = []

    for i in range(0, len(articles), chunk_size):
        chunk = articles[i:i + chunk_size]
        chunks.append(chunk)

    print(f"📊 Split into {len(chunks)} chunks")

    # Save each chunk
    for i, chunk in enumerate(chunks, 1):
        filename = f"vector_stores/Internal_Support_Part_{i}_vector_store.json"
        filepath = Path(filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(chunk, f, ensure_ascii=False, indent=2)

        # Check file size
        file_size = os.path.getsize(filepath)
        file_size_mb = file_size / (1024 * 1024)

        print(f"   ✅ Saved: {filename}")
        print(f"      📊 Size: {file_size_mb:.2f} MB, Articles: {len(chunk)}")

        if file_size_mb > 10:
            print(f"      ⚠️  Still over 10MB limit!")

    # Update the upload guide
    update_upload_guide(len(chunks))

    print("\n🎯 Internal Support splitting complete!")
    print(f"   📁 {len(chunks)} files created in vector_stores/")
    print(f"   📋 Updated: vector_stores/Vector_Store_Upload_Guide.md")

def update_upload_guide(num_parts):
    """Update the upload guide with the split Internal Support files."""

    guide_path = Path("vector_stores/Vector_Store_Upload_Guide.md")

    if guide_path.exists():
        with open(guide_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace the Internal Support section
        old_section = "### Internal Support\n- **File**: `Internal_Support_vector_store.json`\n- **Articles**: 1341\n- **Size**: 24.81 MB\n- **Description**: Support team procedures, troubleshooting, and internal documentation"

        new_section = "### Internal Support (Split into multiple files)\n"
        for i in range(1, num_parts + 1):
            # Estimate size (roughly 24.81 MB / num_parts)
            estimated_size = 24.81 / num_parts
            new_section += f"- **File**: `Internal_Support_Part_{i}_vector_store.json`\n- **Articles**: ~{1341 // num_parts}\n- **Size**: ~{estimated_size:.1f} MB\n- **Description**: Internal Support documentation (Part {i})\n"

        new_section += "- **Description**: Support team procedures, troubleshooting, and internal documentation (split across multiple files)"

        updated_content = content.replace(old_section, new_section)

        with open(guide_path, "w", encoding="utf-8") as f:
            f.write(updated_content)

        print("   ✅ Updated upload guide with split files")

def main():
    """Main function."""
    split_internal_support()

if __name__ == "__main__":
    main()

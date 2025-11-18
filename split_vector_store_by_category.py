"""
Script to split the complete help database into multiple vector store files
that comply with OpenAI's 10MB per file limit.
"""

import json
import os
from pathlib import Path
from collections import defaultdict

def load_consolidated_articles():
    """Load the consolidated articles file."""
    print("🔍 Loading consolidated articles...")

    with open("complete_help_vector_store.json", "r", encoding="utf-8") as f:
        articles = json.load(f)

    print(f"✅ Loaded {len(articles)} articles")
    return articles

def group_articles_by_main_category(articles):
    """Group articles by their main category for splitting."""

    # Define main category groupings
    category_mapping = {
        "Cowis Backoffice": ["Cowis Customer Help", "DdD Customer Help"],
        "Cowis POS": ["RVE - RFA - POSFLOW etc.  Customer Help", "Imagine Documentation"],
        "MStore": ["MStore Customer Help", "MStore User Guide", "MStore Customer FAQs"],
        "Internal Support": ["INTERNAL Support Articles"],
        "Internal MStore": ["INTERNAL MStore Product Information"],
        "RMS": ["RMS Customer Help", "RMSify Customer Help"],
        "Other": ["Omnis Customer Help", "Hardware Support", "Default Category",
                 "How to use this portal and what to expect from Support"],
        "Specialized": ["SmartVision Customer Help", "JobBOSS Customer Help",
                       "Sigma Customer Help", "Alert Manager Customer Help",
                       "ViJi Track Documentation", "Imagine FAQs",
                       "ARCHIVED", "Support Portal"]
    }

    # Group articles
    grouped = defaultdict(list)

    for article in articles:
        category = article.get("category", "Unknown")
        assigned = False

        # Find which main category this belongs to
        for main_cat, sub_cats in category_mapping.items():
            if category in sub_cats:
                grouped[main_cat].append(article)
                assigned = True
                break

        if not assigned:
            grouped["Other"].append(article)

    return grouped

def create_category_vector_store(articles, category_name, output_dir="vector_stores"):
    """Create a vector store file for a specific category."""

    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)

    # Sanitize filename
    safe_name = category_name.replace(" ", "_").replace("/", "_")
    filename = f"{safe_name}_vector_store.json"
    filepath = Path(output_dir) / filename

    print(f"💾 Creating {category_name} vector store ({len(articles)} articles)...")

    # Save as JSON array
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    # Check file size
    file_size = os.path.getsize(filepath)
    file_size_mb = file_size / (1024 * 1024)

    print(f"   ✅ Saved: {filepath}")
    print(f"   📊 Size: {file_size_mb:.2f} MB")

    if file_size_mb > 10:
        print(f"   ⚠️  Still over 10MB limit! Consider further splitting {category_name}")

    return filepath, file_size_mb

def create_upload_guide(grouped_articles, output_dir="vector_stores"):
    """Create a comprehensive upload guide."""

    guide_content = f"""# Cowis Help Database - Vector Store Upload Guide

## Overview
The complete Cowis help database has been split into multiple vector store files to comply with OpenAI's 10MB per file limit.

## Files Created:
"""

    total_articles = 0
    total_size = 0

    for category, articles in grouped_articles.items():
        safe_name = category.replace(" ", "_").replace("/", "_")
        filename = f"{safe_name}_vector_store.json"
        filepath = Path(output_dir) / filename

        if filepath.exists():
            file_size = os.path.getsize(filepath)
            file_size_mb = file_size / (1024 * 1024)
            total_size += file_size_mb

            guide_content += f"""
### {category}
- **File**: `{filename}`
- **Articles**: {len(articles)}
- **Size**: {file_size_mb:.2f} MB
- **Description**: {get_category_description(category)}
"""
            total_articles += len(articles)

    guide_content += f"""

## Total Statistics:
- **Total Articles**: {total_articles}
- **Total Size**: {total_size:.2f} MB
- **Files Created**: {len(grouped_articles)}

## Upload Instructions:

### Step 1: Create Vector Stores
For each file above, create a separate vector store in OpenAI:

1. Go to https://platform.openai.com/
2. Navigate to **"Storage" → "Vector Stores"**
3. Click **"Create"** for each category
4. Use naming convention: "Cowis Help - [Category Name]"

### Step 2: Upload Files
1. For each vector store, click **"Upload files"**
2. Select the corresponding JSON file
3. OpenAI will create embeddings automatically

### Step 3: Connect to Assistant
1. Create or edit your ChatGPT assistant
2. In the **"Knowledge"** section, you can:
   - Select multiple vector stores
   - Or create separate assistants for different categories

## Category Descriptions:
{get_all_category_descriptions()}

## Tips:
- All files are under 10MB limit
- Each category focuses on specific Cowis products/systems
- You can upload all vector stores to one assistant for comprehensive coverage
- Or create specialized assistants for different product areas

## File Locations:
All vector store files are in the `{output_dir}/` directory, ready for upload.
"""

    guide_file = Path(output_dir) / "Vector_Store_Upload_Guide.md"
    with open(guide_file, "w", encoding="utf-8") as f:
        f.write(guide_content)

    print(f"\n📋 Upload guide created: {guide_file}")

def get_category_description(category):
    """Get description for a category."""
    descriptions = {
        "Cowis Backoffice": "Core Cowis backoffice system help articles",
        "Cowis POS": "Point of Sale systems including Imagine and RVE",
        "MStore": "MStore retail management system articles",
        "Internal Support": "Internal support documentation and procedures",
        "Internal MStore": "Internal MStore product information",
        "RMS": "Retail Management System articles",
        "Other": "Miscellaneous help articles",
        "Specialized": "Specialized product documentation (SmartVision, JobBOSS, etc.)"
    }
    return descriptions.get(category, f"{category} help articles")

def get_all_category_descriptions():
    """Get all category descriptions formatted."""
    descriptions = """
### Category Details:

- **Cowis Backoffice**: Core business management, inventory, and administrative functions
- **Cowis POS**: Point of Sale systems, transaction processing, and retail operations
- **MStore**: Complete retail management solution for stores and chains
- **Internal Support**: Support team procedures, troubleshooting, and internal documentation
- **Internal MStore**: Product information and technical details for internal use
- **RMS**: Retail Management System for inventory and sales analytics
- **Other**: General help articles and miscellaneous documentation
- **Specialized**: Product-specific documentation for niche systems and tools
"""
    return descriptions

def main():
    """Main function."""

    print("🚀 Splitting complete help database into multiple vector stores...\n")

    # Load consolidated articles
    articles = load_consolidated_articles()

    # Group by main categories
    grouped = group_articles_by_main_category(articles)

    print(f"📊 Split into {len(grouped)} main categories:")
    for category, category_articles in grouped.items():
        print(f"   • {category}: {len(category_articles)} articles")

    # Create output directory
    output_dir = "vector_stores"
    Path(output_dir).mkdir(exist_ok=True)

    # Create vector store files for each category
    created_files = {}
    for category, category_articles in grouped.items():
        filepath, size_mb = create_category_vector_store(category_articles, category, output_dir)
        created_files[category] = {"file": filepath, "size": size_mb, "articles": len(category_articles)}

    # Create upload guide
    create_upload_guide(grouped, output_dir)

    print("\n🎯 Vector store splitting complete!")
    print(f"   📁 Files created in: {output_dir}/")
    print(f"   📋 Check: {output_dir}/Vector_Store_Upload_Guide.md")

    # Summary
    print("\n📊 Summary:")
    total_articles = sum(info["articles"] for info in created_files.values())
    total_size = sum(info["size"] for info in created_files.values())

    print(f"   • Total articles: {total_articles}")
    print(f"   • Total size: {total_size:.2f} MB")
    print(f"   • Files created: {len(created_files)}")

    # Check all files are under 10MB
    over_limit = [cat for cat, info in created_files.items() if info["size"] > 10]
    if over_limit:
        print(f"   ⚠️  Categories over 10MB limit: {over_limit}")
        print("   Consider further splitting these categories")
    else:
        print("   ✅ All files are under the 10MB limit!")

if __name__ == "__main__":
    main()

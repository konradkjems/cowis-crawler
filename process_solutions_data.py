"""
Script to process the entire Solutions.json file and organize all articles by category.
This will create a comprehensive organization of all help articles from Freshdesk.
"""

import json
import os
import re
from pathlib import Path

def load_solutions_data():
    """Load the entire Solutions.json file."""
    print("🔍 Loading Solutions.json (42MB file)...")
    with open("Solutions.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"✅ Loaded {len(data)} categories")
    return data

def extract_all_articles(data):
    """Extract all articles from the nested Freshdesk structure."""
    all_articles = []

    print("📊 Processing all articles...")

    for category_item in data:
        category = category_item['category']
        category_name = category.get('name', 'Unknown Category')

        print(f"  📁 Processing category: {category_name}")

        for folder in category.get('all_folders', []):
            folder_name = folder.get('name', 'Unknown Folder')

            for article in folder.get('articles', []):
                # Extract clean text from desc_un_html (remove HTML tags)
                desc_un_html = article.get('desc_un_html', '')
                clean_text = ""
                if desc_un_html:
                    # Simple HTML tag removal using regex
                    clean_text = re.sub(r'<[^>]+>', '', desc_un_html)
                    # Clean up extra whitespace
                    clean_text = re.sub(r'\s+', ' ', clean_text).strip()

                # Create article entry
                article_entry = {
                    "id": article.get('id'),
                    "title": article.get('title', ''),
                    "text": clean_text,
                    "category": category_name,
                    "folder": folder_name,
                    "created_at": article.get('created_at'),
                    "updated_at": article.get('updated_at'),
                    "status": article.get('status'),
                    "tags": article.get('tags', []),
                    "description": article.get('description', ''),
                    "user_id": article.get('user_id'),
                    "thumbs_up": article.get('thumbs_up', 0),
                    "thumbs_down": article.get('thumbs_down', 0),
                    "hits": article.get('hits', 0),
                    "seo_data": article.get('seo_data', {}),
                    "modified_at": article.get('modified_at'),
                    "modified_by": article.get('modified_by')
                }

                all_articles.append(article_entry)

    print(f"✅ Extracted {len(all_articles)} total articles")
    return all_articles

def organize_articles_by_category(articles):
    """Organize articles by their source category and folder."""
    organized = {}

    for article in articles:
        category_name = article['category']
        folder_name = article['folder']

        if category_name not in organized:
            organized[category_name] = {}

        if folder_name not in organized[category_name]:
            organized[category_name][folder_name] = []

        organized[category_name][folder_name].append(article)

    return organized

def identify_main_categories():
    """Identify main category groupings based on existing structure."""
    # Based on the existing Cowis structure, map categories to main groups
    main_category_mapping = {
        # Cowis Backoffice categories
        "Cowis Customer Help": "Cowis Backoffice",
        "DdD Customer Help": "Cowis Backoffice",

        # POS categories
        "Imagine Documentation": "Cowis POS",
        "RVE - RFA - POSFLOW etc.  Customer Help": "Cowis POS",

        # Webshop categories
        # (None currently identified as webshop from Solutions.json)

        # Other categories stay as-is or go to general
        "INTERNAL Support Articles": "Internal Support",
        "MStore Customer Help": "MStore",
        "MStore User Guide": "MStore",
        "MStore Customer FAQs": "MStore",
        "RMS Customer Help": "RMS",
        "RMSify Customer Help": "RMS",
        "Alert Manager Customer Help": "Alert Manager",
        "SmartVision Customer Help": "SmartVision",
        "JobBOSS Customer Help": "JobBOSS",
        "Sigma Customer Help": "Sigma",
        "ViJi Track Documentation": "ViJi Track",
        "How to use this portal and what to expect from Support": "Support Portal",
        "Omnis Customer Help": "Omnis",
        "INTERNAL MStore Product Information": "Internal MStore",
        "ARCHIVED": "Archived",
        "Imagine FAQs": "Imagine",
        "Default Category": "Default"
    }

    return main_category_mapping

def organize_by_main_category(articles, main_mapping):
    """Organize articles by main categories."""
    organized = {}

    for article in articles:
        category_name = article['category']
        main_category = main_mapping.get(category_name, "Other")

        if main_category not in organized:
            organized[main_category] = {}

        sub_category = category_name
        folder_name = article['folder']

        if sub_category not in organized[main_category]:
            organized[main_category][sub_category] = {}

        if folder_name not in organized[main_category][sub_category]:
            organized[main_category][sub_category][folder_name] = []

        organized[main_category][sub_category][folder_name].append(article)

    return organized

def sanitize_filename(name):
    """Sanitize folder/filename by removing invalid characters."""
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()

def save_organized_articles(organized_articles):
    """Save articles in organized folder structure."""
    base_dir = Path("Solutions_Organized")
    base_dir.mkdir(exist_ok=True)

    total_articles = 0
    main_category_stats = {}

    print("\n💾 Saving organized articles...")

    # Save by main category
    for main_cat, sub_categories in organized_articles.items():
        main_dir = base_dir / sanitize_filename(main_cat)
        main_dir.mkdir(exist_ok=True)

        main_total = 0

        for sub_cat, folders in sub_categories.items():
            sub_dir = main_dir / sanitize_filename(sub_cat)
            sub_dir.mkdir(exist_ok=True)

            sub_total = 0

            for folder_name, articles in folders.items():
                folder_file = sub_dir / f"{sanitize_filename(folder_name)}.json"

                with open(folder_file, "w", encoding="utf-8") as f:
                    json.dump(articles, f, ensure_ascii=False, indent=2)

                print(f"    ✅ Saved {len(articles)} articles to {folder_file}")
                sub_total += len(articles)

            # Save subcategory index
            sub_index = sub_dir / "index.json"
            sub_index_data = {
                "main_category": main_cat,
                "sub_category": sub_cat,
                "total_articles": sub_total,
                "folders": {folder: len(articles) for folder, articles in folders.items()}
            }

            with open(sub_index, "w", encoding="utf-8") as f:
                json.dump(sub_index_data, f, ensure_ascii=False, indent=2)

            print(f"  📁 {sub_cat}: {sub_total} articles in {len(folders)} folders")
            main_total += sub_total

        # Save main category index
        main_index = main_dir / "index.json"
        main_index_data = {
            "main_category": main_cat,
            "total_articles": main_total,
            "sub_categories": {sub: sum(len(articles) for articles in folders.values())
                             for sub, folders in sub_categories.items()}
        }

        with open(main_index, "w", encoding="utf-8") as f:
            json.dump(main_index_data, f, ensure_ascii=False, indent=2)

        main_category_stats[main_cat] = main_total
        total_articles += main_total
        print(f"🏷️  {main_cat}: {main_total} articles in {len(sub_categories)} subcategories")

    # Save master index
    master_index = {
        "total_articles": total_articles,
        "main_categories": list(main_category_stats.keys()),
        "category_counts": main_category_stats,
        "source_file": "Solutions.json",
        "processed_at": "2025-11-18"
    }

    with open(base_dir / "index.json", "w", encoding="utf-8") as f:
        json.dump(master_index, f, ensure_ascii=False, indent=2)

    print(f"\n🎯 Complete Solutions.json processing finished!")
    print(f"   📊 Total articles processed: {total_articles}")
    print(f"   📂 Organized in {len(organized_articles)} main categories")
    print(f"   📁 Saved to: {base_dir}/")

    return total_articles

def main():
    """Main function."""
    print("🚀 Starting comprehensive Solutions.json processing...\n")

    # Load data
    data = load_solutions_data()

    # Extract all articles
    all_articles = extract_all_articles(data)

    if not all_articles:
        print("❌ No articles found!")
        return

    # Get main category mapping
    main_mapping = identify_main_categories()

    # Organize by main categories
    organized = organize_by_main_category(all_articles, main_mapping)

    # Save organized articles
    total_processed = save_organized_articles(organized)

    # Get file sizes for comparison
    solutions_size = os.path.getsize("Solutions.json") / (1024 * 1024)  # MB
    organized_size = sum(
        os.path.getsize(f) for f in Path("Solutions_Organized").rglob("*.json")
    ) / (1024 * 1024)  # MB

    print("\n📈 Summary:")
    print(f"   Original Solutions.json: {solutions_size:.2f} MB")
    print(f"   Organized data: {organized_size:.2f} MB")
    print(f"   Articles processed: {total_processed}")

if __name__ == "__main__":
    main()

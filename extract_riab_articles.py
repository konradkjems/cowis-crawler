"""
Script to extract RIAB-related articles from Solutions.json and organize them into a separate RIAB folder.
RIAB appears to be a specific POS system variant used in various articles.
"""

import json
import os
from pathlib import Path

def extract_riab_articles():
    """Extract all articles containing 'RIAB' from Solutions.json."""

    print("🔍 Loading Solutions.json...")
    with open("Solutions.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    riab_articles = []

    print(f"📊 Processing {len(data)} categories...")

    for item in data:
        cat = item['category']
        cat_name = cat.get('name', 'Unknown Category')

        for folder in cat.get('all_folders', []):
            folder_name = folder.get('name', 'Unknown Folder')

            for article in folder.get('articles', []):
                # Check if article contains RIAB
                title = article.get('title', '').lower()
                desc = article.get('description', '').lower()
                desc_un_html = article.get('desc_un_html', '').lower()

                has_riab = ('riab' in title or 'riab' in desc or 'riab' in desc_un_html)

                if has_riab:
                    # Extract clean text from desc_un_html (remove HTML tags)
                    import re

                    clean_text = ""
                    if desc_un_html:
                        # Simple HTML tag removal using regex
                        clean_text = re.sub(r'<[^>]+>', '', desc_un_html)
                        # Clean up extra whitespace
                        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

                    # Create article entry similar to vector_store format
                    article_entry = {
                        "id": article.get('id'),
                        "title": article.get('title', ''),
                        "text": clean_text,
                        "category": cat_name,
                        "folder": folder_name,
                        "created_at": article.get('created_at'),
                        "updated_at": article.get('updated_at'),
                        "status": article.get('status'),
                        "tags": article.get('tags', [])
                    }

                    riab_articles.append(article_entry)

    return riab_articles

def organize_by_category(articles):
    """Organize RIAB articles by their source category and folder."""

    organized = {}

    for article in articles:
        cat_name = article['category']
        folder_name = article['folder']

        if cat_name not in organized:
            organized[cat_name] = {}

        if folder_name not in organized[cat_name]:
            organized[cat_name][folder_name] = []

        organized[cat_name][folder_name].append(article)

    return organized

def save_riab_articles(organized_articles):
    """Save RIAB articles in organized folder structure."""

    riab_dir = Path("RIAB")
    riab_dir.mkdir(exist_ok=True)

    total_articles = 0

    print("\n💾 Saving RIAB articles...")

    # Save by category
    for cat_name, folders in organized_articles.items():
        cat_dir = riab_dir / sanitize_filename(cat_name)
        cat_dir.mkdir(exist_ok=True)

        cat_articles = []

        for folder_name, articles in folders.items():
            folder_file = cat_dir / f"{sanitize_filename(folder_name)}.json"

            with open(folder_file, "w", encoding="utf-8") as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)

            print(f"  ✅ Saved {len(articles)} articles to {folder_file}")
            cat_articles.extend(articles)

        # Save category index
        index_file = cat_dir / "index.json"
        index_data = {
            "category": cat_name,
            "total_articles": len(cat_articles),
            "folders": {folder: len(articles) for folder, articles in folders.items()}
        }

        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)

        total_articles += len(cat_articles)
        print(f"  📁 {cat_name}: {len(cat_articles)} articles in {len(folders)} folders")

    # Save main index
    main_index = {
        "riab_articles_total": total_articles,
        "categories": list(organized_articles.keys()),
        "category_counts": {cat: sum(len(articles) for articles in folders.values())
                           for cat, folders in organized_articles.items()}
    }

    with open(riab_dir / "index.json", "w", encoding="utf-8") as f:
        json.dump(main_index, f, ensure_ascii=False, indent=2)

    print(f"\n🎯 RIAB extraction complete!")
    print(f"   📊 Total RIAB articles: {total_articles}")
    print(f"   📂 Organized in {len(organized_articles)} categories")
    print(f"   📁 Saved to: {riab_dir}/")

def sanitize_filename(name):
    """Sanitize folder/filename by removing invalid characters."""
    import re
    # Replace invalid characters with underscores
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()

def main():
    """Main function."""
    print("🚀 Starting RIAB article extraction...\n")

    # Extract RIAB articles
    riab_articles = extract_riab_articles()
    print(f"✅ Found {len(riab_articles)} RIAB-related articles")

    if not riab_articles:
        print("❌ No RIAB articles found!")
        return

    # Organize by category/folder
    organized = organize_by_category(riab_articles)

    # Save organized articles
    save_riab_articles(organized)

if __name__ == "__main__":
    main()

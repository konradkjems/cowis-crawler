#!/usr/bin/env python3
"""
Script to clean and transform cowis helper category.json into vector store format
"""

import json
import re
import html
from bs4 import BeautifulSoup

def extract_images_from_html(html_content):
    """Extract image URLs from HTML content"""
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    images = []

    for img in soup.find_all('img'):
        src = img.get('src')
        if src:
            images.append(src)

    return images

def clean_html_text(html_content):
    """Convert HTML to clean text"""
    if not html_content:
        return ""

    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    # Get text and clean it
    text = soup.get_text()

    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Decode HTML entities
    text = html.unescape(text)

    return text

def process_cowis_helper(input_file, output_file):
    """Process the cowis helper category JSON and create vector store format"""

    print(f"Reading {input_file}...")

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    category = data['category']
    category_name = category['name']

    vector_store = []

    print(f"Processing articles from category: {category_name}")

    for folder in category['all_folders']:
        folder_name = folder['name']

        for article in folder['articles']:
            # Extract images from HTML description
            images = extract_images_from_html(article.get('description', ''))

            # Clean text content
            text = clean_html_text(article.get('description', ''))

            # Create vector store entry
            entry = {
                "title": article.get('title', ''),
                "text": text,
                "category": category_name,
                "subcategory": folder_name,
                "source": "Cowis Help Database",
                "url": None,
                "images": images,
                "has_images": len(images) > 0,
                "image_count": len(images),
                "created_at": article.get('created_at'),
                "updated_at": article.get('updated_at'),
                "id": article.get('id'),
                "tags": article.get('tags', [])
            }

            vector_store.append(entry)

    print(f"Processed {len(vector_store)} articles")

    # Save to output file
    print(f"Saving to {output_file}...")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(vector_store, f, indent=2, ensure_ascii=False)

    print(f"Done! Saved {len(vector_store)} articles to {output_file}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python clean_cowis_helper.py <input_file> <output_file>")
        print("Example: python clean_cowis_helper.py 'cowis helper category.json' 'cowis_helper_vector_store.json'")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        process_cowis_helper(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


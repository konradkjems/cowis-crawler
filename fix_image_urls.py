"""
Script til at rette forkerte image URLs i eksisterende JSON-filer.

Problemet: Billed-URL'er blev scrapet som:
https://knowledge.cowis.net/content/23/27/images/knowledgebase_data/...

Men skal være:
https://knowledge.cowis.net/images/knowledgebase_data/...
"""

import json
import os
from pathlib import Path
import re

def fix_image_urls_in_article(article):
    """Retter image URLs i en artikel."""
    if "images" not in article or not article["images"]:
        return article, False
    
    fixed = False
    fixed_images = []
    
    for img_url in article["images"]:
        # Tjek om URL'en er forkert formateret
        # Forkert: https://knowledge.cowis.net/content/XX/XX/de/images/...
        # Korrekt: https://knowledge.cowis.net/images/...
        
        if "/content/" in img_url and "/images/" in img_url:
            # Extract /images/... delen
            match = re.search(r'/images/(.+)$', img_url)
            if match:
                # Byg korrekt URL
                corrected_url = f"https://knowledge.cowis.net/images/{match.group(1)}"
                fixed_images.append(corrected_url)
                fixed = True
                print(f"   Rettet: {img_url[:80]}... → {corrected_url[:80]}...")
            else:
                # Hvis vi ikke kan matche, behold originalen
                fixed_images.append(img_url)
        else:
            # URL'en er allerede korrekt eller er en anden form
            fixed_images.append(img_url)
    
    article["images"] = fixed_images
    return article, fixed

def fix_category_file(json_file_path):
    """Retter image URLs i en kategori JSON-fil."""
    print(f"📄 Behandler: {json_file_path.name}")
    
    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            articles = json.load(f)
        
        fixed_count = 0
        total_fixed_images = 0
        
        for article in articles:
            fixed_article, was_fixed = fix_image_urls_in_article(article)
            if was_fixed:
                fixed_count += 1
                total_fixed_images += len([img for img in article["images"] if "/content/" in img and "/images/" in img])
            # Erstat artiklen
            articles[articles.index(article)] = fixed_article
        
        if fixed_count > 0:
            # Gem den rettede fil
            with open(json_file_path, "w", encoding="utf-8") as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            print(f"   ✅ Rettet {fixed_count} artikler med {total_fixed_images} billeder")
            return fixed_count, total_fixed_images
        
        return 0, 0
        
    except Exception as e:
        print(f"   ⚠️  Fejl ved behandling af {json_file_path.name}: {e}")
        return 0, 0

def fix_all_category_files():
    """Retter alle kategori JSON-filer."""
    main_categories = ["Cowis Backoffice", "Cowis POS", "Cowis Webshop"]
    total_articles_fixed = 0
    total_images_fixed = 0
    
    print("🔧 Starter rettelse af image URLs...\n")
    
    for main_dir in main_categories:
        categories_dir = Path(main_dir) / "categories"
        
        if not categories_dir.exists():
            print(f"⚠️  Mappe ikke fundet: {categories_dir}")
            continue
        
        print(f"📁 Behandler: {main_dir}")
        
        json_files = list(categories_dir.glob("*.json"))
        json_files = [f for f in json_files if f.name != "index.json"]
        
        for json_file in json_files:
            articles_fixed, images_fixed = fix_category_file(json_file)
            total_articles_fixed += articles_fixed
            total_images_fixed += images_fixed
    
    return total_articles_fixed, total_images_fixed

def fix_vector_store_file():
    """Retter vector_store_data.json filen."""
    json_file = Path("vector_store_data.json")
    
    if not json_file.exists():
        print("⚠️  vector_store_data.json ikke fundet - springer over")
        return 0, 0
    
    print(f"\n📄 Behandler: {json_file.name}")
    
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            articles = json.load(f)
        
        fixed_count = 0
        total_fixed_images = 0
        
        for article in articles:
            fixed_article, was_fixed = fix_image_urls_in_article(article)
            if was_fixed:
                fixed_count += 1
                # Tæl hvor mange billeder der blev rettet
                old_images = article.get("images", [])
                new_images = fixed_article.get("images", [])
                for i, old_img in enumerate(old_images):
                    if "/content/" in old_img and "/images/" in old_img:
                        total_fixed_images += 1
            # Erstat artiklen
            articles[articles.index(article)] = fixed_article
        
        if fixed_count > 0:
            # Gem den rettede fil
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            print(f"   ✅ Rettet {fixed_count} artikler med {total_fixed_images} billeder")
        
        return fixed_count, total_fixed_images
        
    except Exception as e:
        print(f"   ⚠️  Fejl ved behandling af {json_file.name}: {e}")
        return 0, 0

def fix_main_json_file():
    """Retter den samlede cowis_data_with_embeddings.json fil hvis den findes."""
    json_file = Path("cowis_data_with_embeddings.json")
    
    if not json_file.exists():
        print("⚠️  cowis_data_with_embeddings.json ikke fundet - springer over")
        return 0, 0
    
    print(f"\n📄 Behandler: {json_file.name}")
    
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            articles = json.load(f)
        
        fixed_count = 0
        total_fixed_images = 0
        
        for article in articles:
            fixed_article, was_fixed = fix_image_urls_in_article(article)
            if was_fixed:
                fixed_count += 1
                for img in article.get("images", []):
                    if "/content/" in img and "/images/" in img:
                        total_fixed_images += 1
            articles[articles.index(article)] = fixed_article
        
        if fixed_count > 0:
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            print(f"   ✅ Rettet {fixed_count} artikler med {total_fixed_images} billeder")
        
        return fixed_count, total_fixed_images
        
    except Exception as e:
        print(f"   ⚠️  Fejl ved behandling af {json_file.name}: {e}")
        return 0, 0

def main():
    """Hovedfunktion."""
    print("🔧 Rettelse af forkerte image URLs\n")
    print("=" * 60)
    
    # Ret kategori-filer
    cat_articles_fixed, cat_images_fixed = fix_all_category_files()
    
    # Ret vector_store_data.json
    vec_articles_fixed, vec_images_fixed = fix_vector_store_file()
    
    # Ret cowis_data_with_embeddings.json
    main_articles_fixed, main_images_fixed = fix_main_json_file()
    
    # Opsummering
    total_articles = cat_articles_fixed + vec_articles_fixed + main_articles_fixed
    total_images = cat_images_fixed + vec_images_fixed + main_images_fixed
    
    print("\n" + "=" * 60)
    print("✅ Rettelse fuldført!")
    print(f"\n📊 Opsummering:")
    print(f"   Kategori-filer: {cat_articles_fixed} artikler, {cat_images_fixed} billeder")
    print(f"   vector_store_data.json: {vec_articles_fixed} artikler, {vec_images_fixed} billeder")
    print(f"   cowis_data_with_embeddings.json: {main_articles_fixed} artikler, {main_images_fixed} billeder")
    print(f"\n   TOTAL: {total_articles} artikler med {total_images} rettede billeder")

if __name__ == "__main__":
    main()


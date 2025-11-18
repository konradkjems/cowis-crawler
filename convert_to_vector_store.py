"""
Script til at konvertere JSON-filer til Vector Store format (JSON).
Dette script læser alle artikler fra kategorimapperne og konverterer dem
til JSON format der kan uploades til OpenAI Vector Store.
OpenAI laver embeddings automatisk fra text feltet.
"""

import json
import os
from pathlib import Path

def convert_articles_to_vector_store():
    """Konverterer alle artikler fra JSON-filer til Vector Store format."""
    all_items = []
    
    # Gennemgå alle hovedkategorier
    main_categories = ["Cowis Backoffice", "Cowis POS", "Cowis Webshop"]
    
    for main_dir in main_categories:
        categories_dir = Path(main_dir) / "categories"
        
        if not categories_dir.exists():
            print(f"⚠️  Mappe ikke fundet: {categories_dir}")
            continue
        
        print(f"\n📁 Behandler: {main_dir}")
        
        # Gennemgå alle JSON-filer i categories mappen
        json_files = list(categories_dir.glob("*.json"))
        json_files = [f for f in json_files if f.name != "index.json"]
        
        for json_file in json_files:
            print(f"   📄 Læser: {json_file.name}")
            
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    articles = json.load(f)
                
                for article in articles:
                    # Format for OpenAI Vector Store
                    # OpenAI laver embeddings automatisk fra text feltet
                    # Vi gemmer kun det data der er relevant for søgning og display
                    item = {
                        "url": article["url"],
                        "text": article["text"],
                        "images": article.get("images", []),  # Behold som array
                        "main_category": main_dir,
                        "category_file": json_file.stem,
                        "has_images": len(article.get("images", [])) > 0,
                        "image_count": len(article.get("images", []))
                        # Embeddings er ikke nødvendige - OpenAI laver dem automatisk
                    }
                    
                    all_items.append(item)
                    
            except Exception as e:
                print(f"   ⚠️  Fejl ved læsning af {json_file.name}: {e}")
                continue
    
    return all_items

def save_to_json(items, filename="vector_store_data.json"):
    """Gemmer items som JSON fil (array af artikler)."""
    print(f"\n💾 Gemmer {len(items)} artikler til {filename}...")
    
    # Gem som JSON array
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    
    # Tjek filstørrelse
    file_size = os.path.getsize(filename)
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"✅ Fil gemt: {filename}")
    print(f"   📊 Størrelse: {file_size_mb:.2f} MB")
    print(f"   📝 Antal artikler: {len(items)}")
    
    return filename

def main():
    """Hovedfunktion."""
    print("🚀 Starter konvertering til Vector Store format...\n")
    
    # Konverter artikler
    items = convert_articles_to_vector_store()
    
    if not items:
        print("\n⚠️  Ingen artikler fundet!")
        return
    
    print(f"\n✅ Fundet {len(items)} artikler i alt")
    
    # Gem som JSON
    json_file = save_to_json(items)
    
    print(f"\n✅ Konvertering fuldført!")
    print(f"\n📤 Næste skridt:")
    print(f"   1. Upload {json_file} til OpenAI Vector Store")
    print(f"   2. Knyt Vector Store til din Prompt")

if __name__ == "__main__":
    main()


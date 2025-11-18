"""
Script to consolidate all RIAB articles into a single JSON file formatted for OpenAI Vector Store upload.
This creates a single file with all 53 RIAB articles ready for upload to ChatGPT.
"""

import json
import os
from pathlib import Path

def consolidate_riab_articles():
    """Consolidate all RIAB articles into a single array for vector store."""

    riab_dir = Path("RIAB")
    all_articles = []

    print("🔍 Consolidating RIAB articles for Vector Store...")

    # Find all JSON files (excluding index files)
    json_files = []
    for json_file in riab_dir.rglob("*.json"):
        if json_file.name != "index.json":
            json_files.append(json_file)

    print(f"📁 Found {len(json_files)} article files to process")

    total_articles = 0

    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                articles = json.load(f)

            for article in articles:
                # Format for OpenAI Vector Store
                # OpenAI automatically creates embeddings from the "text" field
                vector_item = {
                    # Primary content for embeddings
                    "text": article["text"],

                    # Metadata (can be used for filtering/search)
                    "title": article["title"],
                    "category": article["category"],
                    "folder": article["folder"],
                    "id": article["id"],
                    "created_at": article["created_at"],
                    "updated_at": article["updated_at"],

                    # Additional metadata
                    "source": "RIAB",
                    "tags": article.get("tags", []),
                    "status": article.get("status", 0)
                }

                all_articles.append(vector_item)
                total_articles += 1

        except Exception as e:
            print(f"⚠️  Error processing {json_file}: {e}")
            continue

    print(f"✅ Consolidated {total_articles} articles")
    return all_articles

def create_vector_store_file(articles, output_file="riab_vector_store.json"):
    """Create the final vector store JSON file."""

    print(f"\n💾 Saving consolidated file: {output_file}")

    # Save as JSON array (OpenAI Vector Store format)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    # Check file size
    file_size = os.path.getsize(output_file)
    file_size_mb = file_size / (1024 * 1024)

    print(f"✅ File saved: {output_file}")
    print(f"   📊 Size: {file_size_mb:.2f} MB")
    print(f"   📝 Articles: {len(articles)}")

    # OpenAI Vector Store limits
    if file_size_mb > 10:
        print("⚠️  Warning: File size exceeds 10MB OpenAI limit")
        print("   Consider splitting into multiple files")

    return output_file

def validate_articles(articles):
    """Validate that articles have required fields for vector store."""

    print("\n🔍 Validating articles...")

    missing_text = 0
    empty_text = 0
    total_chars = 0

    for i, article in enumerate(articles):
        if "text" not in article:
            missing_text += 1
            continue

        text_content = article["text"]
        if not text_content or text_content.strip() == "":
            empty_text += 1
            continue

        total_chars += len(text_content)

    avg_chars = total_chars / len(articles) if articles else 0

    print(f"   ✅ Articles with text field: {len(articles) - missing_text}")
    print(f"   ⚠️  Articles missing text field: {missing_text}")
    print(f"   ⚠️  Articles with empty text: {empty_text}")
    print(f"   📊 Average text length: {avg_chars:.0f} characters")

    if missing_text > 0 or empty_text > 0:
        print("⚠️  Some articles may not be suitable for vector store")
    else:
        print("✅ All articles validated successfully")

def create_upload_instructions(output_file):
    """Create instructions for uploading to OpenAI."""

    instructions = f"""
# RIAB Vector Store Upload Instructions

## File Created: {output_file}
## Articles: 53 RIAB-related articles
## Format: OpenAI Vector Store compatible

## Upload Steps:

1. **Go to OpenAI Platform**: https://platform.openai.com/
2. **Navigate to Vector Stores**: In your dashboard, go to "Storage" → "Vector Stores"
3. **Create New Vector Store**:
   - Name: "RIAB Chat Assistant"
   - Description: "Retail in a Box (RIAB) help articles for customer support"
4. **Upload File**:
   - Select the `{output_file}` file
   - OpenAI will automatically create embeddings from the "text" field
5. **Connect to Assistant**:
   - Create or edit your ChatGPT assistant
   - In "Knowledge" section, select your new vector store
   - The assistant can now search RIAB articles for answers

## File Structure:
- Each article has a "text" field (used for embeddings)
- Metadata includes: title, category, folder, id, dates
- All articles are tagged as "source": "RIAB"

## Tips:
- The vector store will enable semantic search across all RIAB articles
- Your assistant can provide context-aware answers about RIAB systems
- Consider adding more RIAB-specific articles as needed
"""

    with open("RIAB_Upload_Instructions.md", "w", encoding="utf-8") as f:
        f.write(instructions.strip())

    print(f"\n📋 Upload instructions saved: RIAB_Upload_Instructions.md")

def main():
    """Main function."""

    print("🚀 Consolidating RIAB articles for Vector Store...\n")

    # Consolidate articles
    articles = consolidate_riab_articles()

    if not articles:
        print("❌ No articles found!")
        return

    # Validate articles
    validate_articles(articles)

    # Create vector store file
    output_file = create_vector_store_file(articles, "riab_vector_store.json")

    # Create upload instructions
    create_upload_instructions(output_file)

    print("\n🎯 RIAB consolidation complete!")
    print(f"   📤 Ready to upload: {output_file}")
    print(f"   🤖 Perfect for: RIAB Chat Assistant on ChatGPT")

if __name__ == "__main__":
    main()

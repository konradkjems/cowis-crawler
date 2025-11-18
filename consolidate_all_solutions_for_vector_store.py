"""
Script to consolidate ALL articles from Solutions_Organized into a single JSON file
formatted for OpenAI Vector Store upload. This creates a comprehensive knowledge base.
"""

import json
import os
from pathlib import Path

def consolidate_all_solutions_articles():
    """Consolidate all articles from Solutions_Organized into a single array for vector store."""

    solutions_dir = Path("Solutions_Organized")
    all_articles = []

    print("🔍 Consolidating ALL articles from Solutions_Organized for Vector Store...")

    # Find all JSON files (excluding index files)
    json_files = []
    for json_file in solutions_dir.rglob("*.json"):
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
                    "source": "Cowis Help Database",
                    "tags": article.get("tags", []),
                    "status": article.get("status", 0),
                    "description": article.get("description", ""),
                    "user_id": article.get("user_id"),
                    "thumbs_up": article.get("thumbs_up", 0),
                    "thumbs_down": article.get("thumbs_down", 0),
                    "hits": article.get("hits", 0)
                }

                all_articles.append(vector_item)
                total_articles += 1

        except Exception as e:
            print(f"⚠️  Error processing {json_file}: {e}")
            continue

    print(f"✅ Consolidated {total_articles} articles")
    return all_articles

def create_vector_store_file(articles, output_file="complete_help_vector_store.json"):
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
        print("   Consider splitting into multiple files or removing some content")

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

def create_upload_instructions(output_file, total_articles, file_size_mb):
    """Create instructions for uploading to OpenAI."""

    instructions = f"""
# Complete Cowis Help Database Vector Store Upload Instructions

## File Created: {output_file}
## Articles: {total_articles} help articles
## Size: {file_size_mb:.2f} MB
## Format: OpenAI Vector Store compatible

## Upload Steps:

1. **Go to OpenAI Platform**: https://platform.openai.com/
2. **Navigate to Vector Stores**: In your dashboard, go to "Storage" → "Vector Stores"
3. **Create New Vector Store**:
   - Name: "Cowis Complete Help Database"
   - Description: "Complete Cowis help articles database for comprehensive customer support"
4. **Upload File**:
   - Select the `{output_file}` file
   - OpenAI will automatically create embeddings from the "text" field
5. **Connect to Assistant**:
   - Create or edit your ChatGPT assistant
   - In "Knowledge" section, select your new vector store
   - The assistant can now search across ALL Cowis help articles

## File Structure:
- Each article has a "text" field (used for embeddings)
- Metadata includes: title, category, folder, id, dates, status, tags
- Articles are tagged as "source": "Cowis Help Database"
- Comprehensive coverage of all Cowis products and systems

## Coverage:
- Cowis Backoffice (240 articles)
- Cowis POS/Imagine (615 articles)
- MStore (212 articles)
- Internal Support (1,341 articles)
- And many more categories...

## Tips:
- The vector store enables semantic search across the entire help database
- Your assistant can provide comprehensive answers about any Cowis system
- If file size exceeds 10MB, consider splitting by main categories

## File Size Check:
- Current size: {file_size_mb:.2f} MB
- OpenAI limit: 10 MB per file
- If too large, the script can split by main categories
"""

    with open("Complete_Help_Upload_Instructions.md", "w", encoding="utf-8") as f:
        f.write(instructions.strip())

    print(f"\n📋 Upload instructions saved: Complete_Help_Upload_Instructions.md")

def main():
    """Main function."""

    print("🚀 Consolidating ALL Solutions_Organized articles for Vector Store...\n")

    # Consolidate articles
    articles = consolidate_all_solutions_articles()

    if not articles:
        print("❌ No articles found!")
        return

    # Validate articles
    validate_articles(articles)

    # Create vector store file
    output_file = create_vector_store_file(articles, "complete_help_vector_store.json")

    # Get file size for instructions
    file_size = os.path.getsize(output_file)
    file_size_mb = file_size / (1024 * 1024)

    # Create upload instructions
    create_upload_instructions(output_file, len(articles), file_size_mb)

    print("\n🎯 Complete help database consolidation finished!")
    print(f"   📤 Ready to upload: {output_file}")
    print(f"   🤖 Perfect for: Comprehensive Cowis Help Assistant")

if __name__ == "__main__":
    main()

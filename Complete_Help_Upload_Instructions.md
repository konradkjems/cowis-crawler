# Complete Cowis Help Database Vector Store Upload Instructions

## File Created: complete_help_vector_store.json
## Articles: 2698 help articles
## Size: 41.91 MB
## Format: OpenAI Vector Store compatible

## Upload Steps:

1. **Go to OpenAI Platform**: https://platform.openai.com/
2. **Navigate to Vector Stores**: In your dashboard, go to "Storage" → "Vector Stores"
3. **Create New Vector Store**:
   - Name: "Cowis Complete Help Database"
   - Description: "Complete Cowis help articles database for comprehensive customer support"
4. **Upload File**:
   - Select the `complete_help_vector_store.json` file
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
- Current size: 41.91 MB
- OpenAI limit: 10 MB per file
- If too large, the script can split by main categories
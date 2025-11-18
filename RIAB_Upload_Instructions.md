# RIAB Vector Store Upload Instructions

## File Created: riab_vector_store.json
## Articles: 53 RIAB-related articles
## Format: OpenAI Vector Store compatible

## Upload Steps:

1. **Go to OpenAI Platform**: https://platform.openai.com/
2. **Navigate to Vector Stores**: In your dashboard, go to "Storage" → "Vector Stores"
3. **Create New Vector Store**:
   - Name: "RIAB Chat Assistant"
   - Description: "Retail in a Box (RIAB) help articles for customer support"
4. **Upload File**:
   - Select the `riab_vector_store.json` file
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
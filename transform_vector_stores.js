const fs = require('fs');
const path = require('path');

// HTML cleaning and image extraction utilities
function cleanHtmlContent(html) {
  if (!html) return '';

  // Extract images before cleaning HTML
  const images = [];
  const imgRegex = /<img[^>]+src=["']([^"']+)["'][^>]*>/gi;
  let match;
  while ((match = imgRegex.exec(html)) !== null) {
    images.push(match[1]);
  }

  // Remove HTML tags
  let cleanText = html.replace(/<[^>]*>/g, '');

  // Decode HTML entities
  cleanText = cleanText
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&hellip;/g, '...')
    .replace(/&mdash;/g, '—')
    .replace(/&ndash;/g, '–');

  // Clean up extra whitespace
  cleanText = cleanText.replace(/\s+/g, ' ').trim();

  return { cleanText, images };
}

// Transform vector store item to simplified format
function transformVectorStoreItem(item) {
  const { cleanText, images } = cleanHtmlContent(item.description);

  return {
    title: item.title || '',
    text: item.text || cleanText,
    category: item.category || '',
    subcategory: item.folder || '',
    source: item.source || '',
    url: item.url || null,
    images: images,
    has_images: images.length > 0,
    image_count: images.length,
    created_at: item.created_at,
    updated_at: item.updated_at,
    // Keep only essential metadata
    id: item.id,
    tags: item.tags || []
  };
}

// Transform knowledge base item (already clean)
function transformKnowledgeBaseItem(item) {
  return {
    title: extractTitleFromText(item.text),
    text: item.text,
    category: item.main_category || '',
    subcategory: item.category_file || '',
    source: 'Cowis Knowledge Base',
    url: item.url,
    images: item.images || [],
    has_images: item.has_images || false,
    image_count: item.image_count || 0,
    created_at: null,
    updated_at: null,
    id: null,
    tags: []
  };
}

// Extract title from text (first line or first sentence)
function extractTitleFromText(text) {
  if (!text) return '';
  const lines = text.split('\n').filter(line => line.trim());
  return lines[0]?.trim() || '';
}

// Main transformation function
async function transformAllVectorStores() {
  const vectorStoresDir = './vector_stores';
  const outputFile = './simplified_vector_store.json';

  let allItems = [];

  try {
    // Read knowledge base data first
    console.log('Reading knowledge base data...');
    const knowledgeData = JSON.parse(fs.readFileSync('vector_store_data.json', 'utf8'));
    const transformedKnowledge = knowledgeData.map(transformKnowledgeBaseItem);
    allItems = allItems.concat(transformedKnowledge);
    console.log(`Processed ${transformedKnowledge.length} knowledge base items`);

    // Read all vector store files
    const files = fs.readdirSync(vectorStoresDir);
    const vectorStoreFiles = files.filter(file => file.endsWith('_vector_store.json'));

    console.log(`Found ${vectorStoreFiles.length} vector store files`);

    for (const file of vectorStoreFiles) {
      console.log(`Processing ${file}...`);
      const filePath = path.join(vectorStoresDir, file);
      const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

      const transformedItems = data.map(transformVectorStoreItem);
      allItems = allItems.concat(transformedItems);

      console.log(`  Added ${transformedItems.length} items from ${file}`);
    }

    // Write unified output
    fs.writeFileSync(outputFile, JSON.stringify(allItems, null, 2));
    console.log(`\n✅ Successfully created ${outputFile} with ${allItems.length} total items`);

    // Statistics
    const withImages = allItems.filter(item => item.has_images);
    const categories = [...new Set(allItems.map(item => item.category))];

    console.log('\n📊 Statistics:');
    console.log(`Total items: ${allItems.length}`);
    console.log(`Items with images: ${withImages.length}`);
    console.log(`Categories: ${categories.length}`);
    console.log('Categories:', categories);

  } catch (error) {
    console.error('❌ Error during transformation:', error);
  }
}

// Run the transformation
transformAllVectorStores();


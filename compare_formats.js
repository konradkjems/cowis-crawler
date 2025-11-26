const fs = require('fs');

// Read both files
const vectorData = JSON.parse(fs.readFileSync('vector_store_data.json', 'utf8'));
const internalSupport = JSON.parse(fs.readFileSync('vector_stores/Internal_Support_Part_1_vector_store.json', 'utf8'));

console.log('=== VECTOR_STORE_DATA.JSON STRUCTURE ===');
console.log('Fields:', Object.keys(vectorData[0]));
console.log('Sample item:');
console.log(JSON.stringify(vectorData[0], null, 2));

console.log('\n=== VECTOR STORE FILE STRUCTURE ===');
console.log('Fields:', Object.keys(internalSupport[0]));
console.log('Sample item (first 500 chars of description):');
console.log(internalSupport[0].description.substring(0, 500) + '...');

// Check if description contains HTML
const hasHtml = internalSupport[0].description.includes('<div') || internalSupport[0].description.includes('<p');
console.log('Description contains HTML tags:', hasHtml);

// Extract clean text from HTML (simple approach)
function extractTextFromHtml(html) {
  // Remove HTML tags
  const text = html.replace(/<[^>]*>/g, '').trim();
  // Clean up extra whitespace
  return text.replace(/\s+/g, ' ');
}

const cleanText = extractTextFromHtml(internalSupport[0].description);
console.log('\nClean text (first 300 chars):', cleanText.substring(0, 300) + '...');

// Proposed simplified structure
console.log('\n=== PROPOSED SIMPLIFIED STRUCTURE ===');
const simplifiedItem = {
  title: internalSupport[0].title,
  text: cleanText,
  category: internalSupport[0].category,
  subcategory: internalSupport[0].folder,
  source: internalSupport[0].source,
  url: internalSupport[0].url || null,
  images: [], // Would need to extract from HTML
  has_images: false,
  created_at: internalSupport[0].created_at,
  updated_at: internalSupport[0].updated_at
};

console.log(JSON.stringify(simplifiedItem, null, 2));


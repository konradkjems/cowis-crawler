const fs = require('fs');
const path = require('path');

// Create output directory
const outputDir = 'categorized_vector_stores';
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir);
}

const data = JSON.parse(fs.readFileSync('simplified_vector_store.json', 'utf8'));

// Group by category
const categoryGroups = {};
data.forEach(item => {
  const category = item.category || 'Uncategorized';
  if (!categoryGroups[category]) {
    categoryGroups[category] = [];
  }
  categoryGroups[category].push(item);
});

// Function to create safe filename
function createSafeFilename(category) {
  return category
    .replace(/[^a-zA-Z0-9\s\-_]/g, '') // Remove special chars
    .replace(/\s+/g, '_') // Replace spaces with underscores
    .replace(/_+/g, '_') // Replace multiple underscores with single
    .replace(/^_+|_+$/g, '') // Remove leading/trailing underscores
    .toLowerCase()
    + '_vector_store.json';
}

// Save each category to separate file
let totalProcessed = 0;
const categories = Object.keys(categoryGroups).sort();

console.log(`Splitting ${data.length} items into ${categories.length} categories...`);

categories.forEach(category => {
  const items = categoryGroups[category];
  const filename = createSafeFilename(category);
  const filepath = path.join(outputDir, filename);

  // Write the category data
  fs.writeFileSync(filepath, JSON.stringify(items, null, 2));

  console.log(`✅ ${category}: ${items.length} items → ${filename}`);
  totalProcessed += items.length;
});

console.log(`\n🎉 Successfully split into ${categories.length} files in '${outputDir}' directory`);
console.log(`Total items processed: ${totalProcessed}`);

// Create a summary file
const summary = {
  total_items: data.length,
  total_categories: categories.length,
  categories: categories.map(cat => ({
    name: cat,
    count: categoryGroups[cat].length,
    filename: createSafeFilename(cat)
  })),
  created_at: new Date().toISOString()
};

fs.writeFileSync(path.join(outputDir, 'categories_summary.json'), JSON.stringify(summary, null, 2));
console.log('📋 Created categories_summary.json with overview');


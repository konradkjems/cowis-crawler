const fs = require('fs');

// Read the current vector_store_data.json
const data = JSON.parse(fs.readFileSync('vector_store_data.json', 'utf8'));

console.log('Current structure analysis:');
console.log('Total items:', data.length);
console.log('Sample item structure:');
console.log(JSON.stringify(data[0], null, 2));

// Check what fields are present
const fields = new Set();
data.forEach(item => {
  Object.keys(item).forEach(key => fields.add(key));
});

console.log('All fields found:', Array.from(fields));

// Analyze content to see if there's HTML
console.log('\nContent analysis:');
const sampleText = data[0].text;
console.log('Sample text length:', sampleText.length);
console.log('Contains HTML tags:', sampleText.includes('<') || sampleText.includes('>'));
console.log('First 200 chars of text:', sampleText.substring(0, 200));

// Check images
const withImages = data.filter(item => item.images && item.images.length > 0);
console.log('Items with images:', withImages.length);
console.log('Sample images array:', withImages[0]?.images);


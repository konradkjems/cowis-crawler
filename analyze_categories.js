const fs = require('fs');
const data = JSON.parse(fs.readFileSync('simplified_vector_store.json', 'utf8'));

// Find unique categories
const categories = [...new Set(data.map(item => item.category))];
console.log('Categories found:', categories.length);
console.log('Categories:');
categories.forEach(cat => console.log(' -', cat));

// Count items per category
console.log('\nItems per category:');
const categoryCounts = {};
data.forEach(item => {
  categoryCounts[item.category] = (categoryCounts[item.category] || 0) + 1;
});

Object.entries(categoryCounts)
  .sort((a, b) => b[1] - a[1])
  .forEach(([cat, count]) => {
    console.log(`${cat}: ${count} items`);
  });


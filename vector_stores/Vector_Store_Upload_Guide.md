# Cowis Help Database - Vector Store Upload Guide

## Overview
The complete Cowis help database has been split into multiple vector store files to comply with OpenAI's 10MB per file limit.

## Files Created:

### RMS
- **File**: `RMS_vector_store.json`
- **Articles**: 26
- **Size**: 0.12 MB
- **Description**: Retail Management System articles

### Specialized
- **File**: `Specialized_vector_store.json`
- **Articles**: 149
- **Size**: 2.09 MB
- **Description**: Specialized product documentation (SmartVision, JobBOSS, etc.)

### Internal Support (Split into multiple files)
- **File**: `Internal_Support_Part_1_vector_store.json`
- **Articles**: ~335
- **Size**: ~6.2 MB
- **Description**: Internal Support documentation (Part 1)
- **File**: `Internal_Support_Part_2_vector_store.json`
- **Articles**: ~335
- **Size**: ~6.2 MB
- **Description**: Internal Support documentation (Part 2)
- **File**: `Internal_Support_Part_3_vector_store.json`
- **Articles**: ~335
- **Size**: ~6.2 MB
- **Description**: Internal Support documentation (Part 3)
- **File**: `Internal_Support_Part_4_vector_store.json`
- **Articles**: ~336
- **Size**: ~6.2 MB
- **Description**: Internal Support documentation (Part 4)

### Other
- **File**: `Other_vector_store.json`
- **Articles**: 61
- **Size**: 0.65 MB
- **Description**: Miscellaneous help articles

### Internal MStore
- **File**: `Internal_MStore_vector_store.json`
- **Articles**: 54
- **Size**: 0.15 MB
- **Description**: Internal MStore product information

### Cowis POS
- **File**: `Cowis_POS_vector_store.json`
- **Articles**: 615
- **Size**: 8.80 MB
- **Description**: Point of Sale systems including Imagine and RVE

### Cowis Backoffice
- **File**: `Cowis_Backoffice_vector_store.json`
- **Articles**: 240
- **Size**: 1.96 MB
- **Description**: Core Cowis backoffice system help articles

### MStore
- **File**: `MStore_vector_store.json`
- **Articles**: 212
- **Size**: 3.34 MB
- **Description**: MStore retail management system articles


## Total Statistics:
- **Total Articles**: 2698
- **Total Size**: 41.91 MB
- **Files Created**: 11 (Internal Support split into 4 parts)

## Upload Instructions:

### Step 1: Create Vector Stores
For each file above, create a separate vector store in OpenAI:

1. Go to https://platform.openai.com/
2. Navigate to **"Storage" → "Vector Stores"**
3. Click **"Create"** for each category
4. Use naming convention: "Cowis Help - [Category Name]"

### Step 2: Upload Files
1. For each vector store, click **"Upload files"**
2. Select the corresponding JSON file
3. OpenAI will create embeddings automatically

### Step 3: Connect to Assistant
1. Create or edit your ChatGPT assistant
2. In the **"Knowledge"** section, you can:
   - Select multiple vector stores
   - Or create separate assistants for different categories

## Category Descriptions:

### Category Details:

- **Cowis Backoffice**: Core business management, inventory, and administrative functions
- **Cowis POS**: Point of Sale systems, transaction processing, and retail operations
- **MStore**: Complete retail management solution for stores and chains
- **Internal Support**: Support team procedures, troubleshooting, and internal documentation
- **Internal MStore**: Product information and technical details for internal use
- **RMS**: Retail Management System for inventory and sales analytics
- **Other**: General help articles and miscellaneous documentation
- **Specialized**: Product-specific documentation for niche systems and tools


## Tips:
- All files are under 10MB limit
- Each category focuses on specific Cowis products/systems
- You can upload all vector stores to one assistant for comprehensive coverage
- Or create specialized assistants for different product areas

## File Locations:
All vector store files are in the `vector_stores/` directory, ready for upload.

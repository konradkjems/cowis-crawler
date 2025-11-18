# Vector Store Setup Guide

Denne guide forklarer hvordan du konverterer dine JSON-filer til Vector Store format og uploader dem til OpenAI.

## Step 1: Konverter JSON-filer til Vector Store format

Kør scriptet der konverterer alle dine JSON-filer til JSONL format:

```bash
python3 convert_to_vector_store.py
```

Dette laver en fil kaldet `vector_store_data.json` med alle artikler i Vector Store format.

**Output:**
- `vector_store_data.json` - Fil klar til upload (ca. 4-5 MB for ~130 artikler)

## Step 2: Upload til OpenAI Vector Store

Kør upload scriptet:

```bash
python3 upload_to_vector_store.py
```

Dette script:
1. Opretter en Vector Store i OpenAI
2. Uploader JSONL filen
3. Giver dig Vector Store ID til brug med din Prompt

**Output:**
- Vector Store ID (skriv dette ned!)

## Step 3: Brug Vector Store med din Prompt

### Eksempel kode med Prompts (promptID):

```python
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Din Vector Store ID (fra step 2)
VECTOR_STORE_ID = "vs_xxxxx"  # Erstat med din Vector Store ID

# Din Prompt ID (fra platform.openai.com)
PROMPT_ID = "prmpt_xxxxx"  # Erstat med din Prompt ID

# Kald din Prompt med Vector Store
response = client.beta.prompts.completions.create(
    prompt_id=PROMPT_ID,
    model="gpt-4-turbo-preview",
    messages=[
        {
            "role": "user",
            "content": "Hvordan logger jeg ind i Cowis Backoffice?"
        }
    ],
    tools=[{"type": "file_search"}],
    tool_resources={
        "file_search": {
            "vector_store_ids": [VECTOR_STORE_ID]
        }
    }
)

print(response.choices[0].message.content)
```

### Alternativt - Hvis du bruger Chat Completions API direkte:

```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VECTOR_STORE_ID = "vs_xxxxx"

response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[
        {
            "role": "system",
            "content": "Du er en support assistant for Cowis. Brug Vector Store til at finde relevante artikler."
        },
        {
            "role": "user",
            "content": "Hvordan logger jeg ind i Cowis Backoffice?"
        }
    ],
    tools=[{"type": "file_search"}],
    tool_resources={
        "file_search": {
            "vector_store_ids": [VECTOR_STORE_ID]
        }
    }
)

print(response.choices[0].message.content)
```

## Hvad er Vector Store format?

Hver artikel i JSON filen er et objekt med:
- `id`: Unik ID for artiklen
- `values`: Embedding array (1536 tal for text-embedding-3-small)
- `metadata`: 
  - `url`: Artikel URL
  - `text`: Artikel tekst
  - `images`: Komma-separeret liste af billed-URLs
  - `main_category`: "Cowis Backoffice", "Cowis POS", eller "Cowis Webshop"
  - `category_file`: Kategori filnavn
  - `has_images`: Boolean
  - `image_count`: Antal billeder

## Vigtigt om format

OpenAI Vector Stores understøtter `.json` filer, men **ikke** embeddings direkte.
Når du uploader JSON filen, vil OpenAI:
- Læse artiklerne fra JSON filen
- Lave embeddings automatisk baseret på `text` feltet
- Bruge disse embeddings til File Search

**Bemærk:** Dine eksisterende embeddings i JSON filen bruges ikke, men metadata (url, text, images) bevares.

## Opdatering

Hvis du opdaterer dine JSON-filer (nye artikler), kør begge scripts igen.
Bemærk: Dette vil oprette en NY Vector Store. Du kan enten:
- Slette den gamle først i platform.openai.com
- Eller navngive dem forskelligt
- Opdatere din Prompt til at bruge den nye Vector Store ID

## Fejlhåndtering

Hvis upload fejler:
1. Tjek at `vector_store_data.json` eksisterer
2. Tjek at din API key er korrekt i `.env`
3. Tjek at du har rådighed til at oprette Vector Stores i din OpenAI plan


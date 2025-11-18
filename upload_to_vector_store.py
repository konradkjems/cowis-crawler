"""
Script til at uploade JSONL fil til OpenAI Vector Store.
Vector Store kan derefter bruges med Prompts (promptID) i din applikation.
"""

import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Ingen OPENAI_API_KEY fundet i .env")

client = OpenAI(api_key=api_key)

def upload_file_for_vector_store(json_file="vector_store_data.json"):
    """Uploader fil til brug med Vector Store (via File Search)."""
    
    print(f"📤 Uploader {json_file} til OpenAI...")
    
    # Prøv at uploade filen - OpenAI vil automatisk oprette Vector Store når den bruges
    print(f"\n📤 Uploader fil: {json_file}")
    try:
        with open(json_file, "rb") as f:
            file = client.files.create(
                file=f,
                purpose="assistants"  # Brug "assistants" for File Search
            )
        
        print(f"✅ Fil uploaded: {file.id}")
        print(f"   Fil navn: {file.filename}")
        print(f"   Fil størrelse: {file.bytes} bytes")
        
        return file
        
    except Exception as e:
        print(f"❌ Fejl ved upload: {e}")
        raise

def try_create_vector_store():
    """Prøver at oprette Vector Store direkte (kan fejle hvis API ikke understøtter det)."""
    try:
        print("🔨 Prøver at oprette Vector Store via API...")
        vector_store = client.beta.vector_stores.create(
            name="Cowis Knowledge Base",
            description="Cowis Backoffice, POS og Webshop documentation"
        )
        print(f"✅ Vector Store oprettet: {vector_store.id}")
        return vector_store
    except AttributeError:
        print("⚠️  Vector Stores API ikke tilgængelig i denne SDK version")
        print("   Brug i stedet File Search som automatisk opretter Vector Store")
        return None
    except Exception as e:
        print(f"⚠️  Fejl ved oprettelse af Vector Store: {e}")
        return None


def main():
    """Hovedfunktion."""
    json_file = "vector_store_data.json"
    
    if not os.path.exists(json_file):
        print(f"⚠️  Fil ikke fundet: {json_file}")
        print("   Kør først: python3 convert_to_vector_store.py")
        return
    
    print("🚀 Starter upload til OpenAI Vector Store...\n")
    
    try:
        # Prøv først at oprette Vector Store direkte
        vector_store = try_create_vector_store()
        
        # Upload fil
        uploaded_file = upload_file_for_vector_store(json_file)
        
        if vector_store:
            # Hvis Vector Store blev oprettet, tilføj filen
            try:
                print(f"\n🔗 Tilføjer fil til Vector Store...")
                file_batch = client.beta.vector_stores.file_batches.create(
                    vector_store_id=vector_store.id,
                    file_ids=[uploaded_file.id]
                )
                
                print(f"📦 Batch oprettet: {file_batch.id}")
                
                # Vent på at batch er klar
                print("\n⏳ Venter på at batch bliver klar...")
                while file_batch.status in ["in_progress", "queued"]:
                    time.sleep(2)
                    file_batch = client.beta.vector_stores.file_batches.retrieve(
                        vector_store_id=vector_store.id,
                        batch_id=file_batch.id
                    )
                    print(f"   Status: {file_batch.status}...")
                
                if file_batch.status == "completed":
                    print(f"✅ Batch færdig!")
            except Exception as e:
                print(f"⚠️  Kunne ikke tilføje fil til Vector Store: {e}")
                print("   Brug File Search i stedet (automatisk)")
        
        print(f"\n✅ Fuldført!")
        print(f"\n📋 Din fil er klar:")
        print(f"   File ID: {uploaded_file.id}")
        
        if vector_store:
            print(f"   Vector Store ID: {vector_store.id}")
            print(f"\n💡 Næste skridt:")
            print(f"   Brug Vector Store ID i din Prompt:")
            print(f"""
   tool_resources={{"file_search": {{"vector_store_ids": ["{vector_store.id}"]}}}}
   """)
        else:
            print(f"\n💡 Næste skridt (File Search):")
            print(f"   OpenAI opretter automatisk Vector Store når du bruger File Search")
            print(f"   Brug File ID direkte i din Prompt:")
            print(f"""
   tools=[{{"type": "file_search"}}]
   tool_resources={{"file_search": {{"vector_store_ids": []}}}}
   
   ELLER uploade via platform.openai.com og knytte til din Prompt der.
   """)
            print(f"\n📝 Alternativ: Manuelt på platform.openai.com")
            print(f"   1. Gå til platform.openai.com")
            print(f"   2. Opret Vector Store manuelt")
            print(f"   3. Upload {json_file} filen (du kan finde den i denne mappe)")
            print(f"   4. Knyt Vector Store til din Prompt")
        
    except Exception as e:
        print(f"\n❌ Fejl: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()



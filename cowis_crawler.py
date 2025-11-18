import os
import json
import time
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote, urlparse, parse_qs, urlunparse
from openai import OpenAI
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Ingen OPENAI_API_KEY fundet i .env")

client = OpenAI(api_key=api_key)

BASE_URL = "https://knowledge.cowis.net/"

# Cowis Backoffice kategorier
BACKOFFICE_CATEGORIES = [
    # Basiswissen
    "https://knowledge.cowis.net/category/21/basiswissen.html",
    # Handbuch - 1. Einführung
    "https://knowledge.cowis.net/category/23/1&period-einf&uumlhrung.html",
    # Handbuch - 2. Adressen
    "https://knowledge.cowis.net/category/24/2&period-adressen.html",
    # Handbuch - 3. Artikel
    "https://knowledge.cowis.net/category/25/3&period-artikel.html",
    # Handbuch - 4. Wareneingang
    "https://knowledge.cowis.net/category/26/4&period-wareneingang.html",
    # Handbuch - 5. Retoure
    "https://knowledge.cowis.net/category/27/5&period-retoure.html",
    # Handbuch - 6. Order
    "https://knowledge.cowis.net/category/28/6&period-order.html",
    # Handbuch - 7. Auftragsbearbeitung
    "https://knowledge.cowis.net/category/29/7&period-auftragsbearbeitung.html",
    # Handbuch - 8. Zahlungen
    "https://knowledge.cowis.net/category/30/8&period-zahlungen.html",
    # Handbuch - 9. Auswertungen
    "https://knowledge.cowis.net/category/31/9&period-auswertungen.html",
    # Handbuch - 10. Inventur
    "https://knowledge.cowis.net/category/32/10&period-inventur.html",
    # Handbuch - 11. EDI
    "https://knowledge.cowis.net/category/33/11&period-edi.html",
    # Handbuch - 12. Kassenabschlüsse
    "https://knowledge.cowis.net/category/34/12&period-kassenabschl&uumlsse.html",
    # Handbuch - 13. Etikettendruck
    "https://knowledge.cowis.net/category/35/13&period-etikettendruck.html",
    # Handbuch - 14. Einstellungen
    "https://knowledge.cowis.net/category/47/14&period-einstellungen.html",
    # Schnittstellen - E-Commerce
    "https://knowledge.cowis.net/category/46/e_commerce.html",
    # Schnittstellen - EDI
    "https://knowledge.cowis.net/category/50/edi.html",
    # Schnittstellen - Fibu
    "https://knowledge.cowis.net/category/52/fibu.html",
    # Schnittstellen - Stammdatenimport-export
    "https://knowledge.cowis.net/category/53/stammdatenimport_export.html",
    # Systemvoraussetzungen
    "https://knowledge.cowis.net/category/48/systemvoraussetzungen.html"
]

# Cowis POS kategorier
POS_CATEGORIES = [
    # Handbuch
    "https://knowledge.cowis.net/category/37/handbuch.html",
    # Systemvoraussetzungen
    "https://knowledge.cowis.net/category/49/systemvoraussetzungen.html"
]

# Cowis Webshop kategorier
WEBSHOP_CATEGORIES = [
    # Gutscheinverwaltung
    "https://knowledge.cowis.net/category/17/gutscheinverwaltung.html"
]

# Updatebeschreibungen kategorier
UPDATEBESCHREIBUNGEN_CATEGORIES = [
    # DdD Cowis backoffice
    "https://knowledge.cowis.net/category/42/ddd-cowis-backoffice.html",
    # DdD Cowis pos
    "https://knowledge.cowis.net/category/43/ddd-cowis-pos.html",
    # DdD Cowis Webshop
    "https://knowledge.cowis.net/category/44/ddd-cowis-webshop.html"
]

# Samlet liste med mapping til hovedkategori
CATEGORY_MAPPING = {
    "backoffice": BACKOFFICE_CATEGORIES,
    "pos": POS_CATEGORIES,
    "webshop": WEBSHOP_CATEGORIES,
    "updatebeschreibungen": UPDATEBESCHREIBUNGEN_CATEGORIES
}

START_CATEGORIES = BACKOFFICE_CATEGORIES + POS_CATEGORIES + WEBSHOP_CATEGORIES + UPDATEBESCHREIBUNGEN_CATEGORIES

visited_urls = set()
articles = []
category_articles = {}  # Holder styr på artikler per kategori
category_main_map = {}  # Holder styr på hvilken hovedkategori hver kategori tilhører

def normalize_url(url):
    """Fjerner irrelevante query params og normaliserer URL'en."""
    url = unquote(url)
    parsed = urlparse(url)
    clean_path = parsed.path.strip("/")
    # Drop query params helt for at undgå loops
    normalized = urlunparse((parsed.scheme, parsed.netloc, clean_path, "", "", ""))
    return normalized.lower()

def fetch_html(url):
    try:
        # Headers for at browse fra Tyskland
        headers = {
            "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"Fejl ved hentning af {url}: {e}")
        return ""

def extract_article_links(html, base_url):
    """Ekstraherer kun artikel-links fra en kategori-side."""
    soup = BeautifulSoup(html, "html.parser")
    article_links = set()
    
    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = urljoin(base_url, href)
        normalized = normalize_url(full_url)
        
        # Kun artikel-links fra samme domain
        if normalized.startswith(BASE_URL.rstrip("/")) and "/content/" in normalized:
            article_links.add(normalized)
    
    return article_links


def is_category(url):
    return "/category/" in url

def is_article(url):
    return "/content/" in url

def get_main_category(url):
    """Identificerer hovedkategorien baseret på URL."""
    normalized = normalize_url(url)
    
    # For kategorier eller artikler, tjek kategori-ID fra URL
    match = re.search(r'/category/(\d+)/', normalized)
    if match:
        cat_id = int(match.group(1))
        
        # Updatebeschreibungen underkategorier mappes til deres respektive hovedkategorier
        if cat_id == 42:  # Updatebeschreibungen - DdD Cowis backoffice
            return "backoffice"
        if cat_id == 43:  # Updatebeschreibungen - DdD Cowis pos
            return "pos"
        if cat_id == 44:  # Updatebeschreibungen - DdD Cowis Webshop
            return "webshop"
        
        # POS kategori ID'er: 37, 49
        if cat_id == 37 or cat_id == 49:
            return "pos"
        
        # Webshop kategori ID'er: 15, 17
        if cat_id == 15 or cat_id == 17:
            return "webshop"
        
        # Backoffice kategori ID'er: 21, 23-35, 46-48, 50, 52-53
        if cat_id in [21, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 46, 47, 48, 50, 52, 53]:
            return "backoffice"
    
    # Tjek om URL'en er direkte i en af kategorilisterne
    for pos_cat in POS_CATEGORIES:
        pos_normalized = normalize_url(pos_cat)
        if normalized == pos_normalized:
            return "pos"
    
    for webshop_cat in WEBSHOP_CATEGORIES:
        webshop_normalized = normalize_url(webshop_cat)
        if normalized == webshop_normalized:
            return "webshop"
    
    for update_cat in UPDATEBESCHREIBUNGEN_CATEGORIES:
        update_normalized = normalize_url(update_cat)
        if normalized == update_normalized:
            # Map updatebeschreibungen underkategorier til deres respektive hovedkategorier
            if "/category/42/" in normalized:
                return "backoffice"
            if "/category/43/" in normalized:
                return "pos"
            if "/category/44/" in normalized:
                return "webshop"
    
    for backoffice_cat in BACKOFFICE_CATEGORIES:
        backoffice_normalized = normalize_url(backoffice_cat)
        if normalized == backoffice_normalized:
            return "backoffice"
    
    # Default til backoffice hvis usikker
    return "backoffice"

def get_category_name(url):
    """Ekstraherer kategori-navn eller ID fra URL."""
    if is_category(url):
        # Eksempel: /category/8/ddd-cowis-backoffice.html -> ddd-cowis-backoffice
        match = re.search(r'/category/\d+/([^/]+)\.html', url)
        if match:
            return match.group(1)
        # Fallback til kategori-ID
        match = re.search(r'/category/(\d+)/', url)
        if match:
            return f"category_{match.group(1)}"
    # For artikler, find den overordnede kategori fra path
    match = re.search(r'/category/(\d+)/', url)
    if match:
        return f"category_{match.group(1)}"
    return "unknown"

def get_category_from_url_stack(url, category_stack):
    """Finder den nuværende kategori baseret på URL stack."""
    if is_category(url):
        return get_category_name(url)
    # For artikler, brug den seneste kategori i stack
    if category_stack:
        return category_stack[-1]
    return "unknown"

def extract_article_text(html):
    """Ekstraherer artikeltekst fra HTML."""
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    
    # Fjern scripts, styles, navigation og footer elementer
    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()
    
    # Prøv flere strategier for at finde artikelindhold
    # 1. Find h2 med artikel-titel og tag parent content area
    h2 = soup.find("h2")
    if h2:
        # Find det nærmeste content container
        content_parent = h2.find_parent(["div", "main", "article", "section"])
        if content_parent:
            # Fjern eventuelle nested navigation/links sections
            for nav in content_parent.find_all(["nav", "ul"], class_=lambda x: x and ("nav" in str(x).lower() or "menu" in str(x).lower()) if x else False):
                nav.decompose()
            text = content_parent.get_text(separator="\n", strip=True)
            if len(text) > 100:  # Tjek at vi har nok indhold
                return text
    
    # 2. Fallback: Find div med "content" i class eller id
    content_div = soup.find("div", class_=lambda x: x and ("content" in str(x).lower() or "article" in str(x).lower()) if x else False)
    if content_div:
        text = content_div.get_text(separator="\n", strip=True)
        if len(text) > 100:
            return text
    
    # 3. Fallback: Find wrapper og filtrer bedre
    wrapper = soup.find("div", {"id": "wrapper"})
    if wrapper:
        # Fjern navigation, footer og lignende
        for element in wrapper.find_all(["nav", "footer", "header", "aside"]):
            element.decompose()
        text = wrapper.get_text(separator="\n", strip=True)
        # Filtrer væk for kort tekst (sandsynligvis ikke artikelindhold)
        if len(text) > 100:
            return text
    
    # 4. Sidste resort: Find main element
    main = soup.find("main")
    if main:
        text = main.get_text(separator="\n", strip=True)
        if len(text) > 100:
            return text
    
    return ""

def extract_images(html, article_url):
    """Ekstraherer alle billed-URLs fra en artikel-side."""
    if not html:
        return []
    
    soup = BeautifulSoup(html, "html.parser")
    image_urls = []
    
    # Find artikel-indholdet først (samme logik som extract_article_text)
    content_area = None
    h2 = soup.find("h2")
    if h2:
        content_area = h2.find_parent(["div", "main", "article", "section"])
    
    if not content_area:
        content_area = soup.find("div", class_=lambda x: x and ("content" in str(x).lower() or "article" in str(x).lower()) if x else False)
    
    if not content_area:
        content_area = soup.find("div", {"id": "wrapper"})
    
    # Find alle img tags i indholdet (eller hele siden hvis content_area ikke findes)
    search_area = content_area if content_area else soup
    
    for img in search_area.find_all("img"):
        src = img.get("src") or img.get("data-src")  # data-src for lazy-loaded images
        if not src:
            continue
        
        # Konverter relative URL til absolut URL
        # Hvis src starter med / eller images/, brug BASE_URL som base
        # Dette sikrer at /images/... bliver til https://knowledge.cowis.net/images/...
        # og ikke https://knowledge.cowis.net/content/XX/XX/de/images/...
        if src.startswith('http://') or src.startswith('https://'):
            # Allerede en absolut URL
            full_url = src
        elif src.startswith('/'):
            # Absolut path fra websitet root (fx /images/...)
            full_url = urljoin(BASE_URL, src)
        elif src.startswith('images/'):
            # Starter med images/ - skal være /images/ fra root
            full_url = urljoin(BASE_URL, '/' + src)
        elif '/images/' in src:
            # Indeholder /images/ et sted - brug BASE_URL for at sikre korrekt path
            full_url = urljoin(BASE_URL, '/' + src.lstrip('/'))
        else:
            # Relativt til artiklen - brug article_url som base
            full_url = urljoin(article_url, src)
        
        # Filtrer væk tydelige ikoner/logoer baseret på URL path
        src_lower = src.lower()
        if any(excluded in src_lower for excluded in ["icon", "logo", "arrow", "spacer", "pixel.gif", "1x1", "blank.gif"]):
            continue
        
        # Tjek at det ikke er i navigation/header/footer
        parent = img.find_parent(["nav", "header", "footer", "aside"])
        if parent:
            continue
        
        # Tjek billedets størrelse hvis angivet
        width = img.get("width", "")
        height = img.get("height", "")
        
        # Hvis størrelse er angivet, tjek at det ikke er et lille ikon
        if width and width.isdigit():
            if int(width) < 50:
                continue
        if height and height.isdigit():
            if int(height) < 50:
                continue
        
        # Hvis vi når hertil, er det sandsynligvis et indholdsbillede
        image_urls.append(full_url)
    
    # Fjern duplikater og returner
    return list(set(image_urls))

def get_embedding(text):
    try:
        resp = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return resp.data[0].embedding
    except Exception as e:
        print(f"Fejl ved embeddings: {e}")
        return []

def save_category_files():
    """Gemmer separate JSON-filer for hver kategori, organiseret efter hovedkategori."""
    # Organiser kategorier efter hovedkategori
    backoffice_categories = {}
    pos_categories = {}
    webshop_categories = {}
    
    for category_name, cat_articles in category_articles.items():
        if not cat_articles:  # Spring over tomme kategorier
            continue
        
        main_cat = category_main_map.get(category_name, "backoffice")
        
        if main_cat == "pos":
            pos_categories[category_name] = cat_articles
        elif main_cat == "webshop":
            webshop_categories[category_name] = cat_articles
        else:
            backoffice_categories[category_name] = cat_articles
    
    total_articles = 0
    
    # Gem Backoffice kategorier
    if backoffice_categories:
        backoffice_dir = "Cowis Backoffice/categories"
        os.makedirs(backoffice_dir, exist_ok=True)
        backoffice_total = 0
        
        for category_name, cat_articles in backoffice_categories.items():
            filename = f"{backoffice_dir}/{category_name}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(cat_articles, f, ensure_ascii=False, indent=2)
            print(f"[AUTO-SAVE] {len(cat_articles)} artikler gemt i {filename}")
            backoffice_total += len(cat_articles)
        
        # Gem index for Backoffice
        backoffice_index = {
            "main_category": "backoffice",
            "total_articles": backoffice_total,
            "categories": {name: len(articles) for name, articles in backoffice_categories.items()}
        }
        with open(f"{backoffice_dir}/index.json", "w", encoding="utf-8") as f:
            json.dump(backoffice_index, f, ensure_ascii=False, indent=2)
        
        total_articles += backoffice_total
        print(f"[AUTO-SAVE] Totalt {backoffice_total} Backoffice artikler gemt i {len(backoffice_categories)} kategorier")
    
    # Gem POS kategorier
    if pos_categories:
        pos_dir = "Cowis POS/categories"
        os.makedirs(pos_dir, exist_ok=True)
        pos_total = 0
        
        for category_name, cat_articles in pos_categories.items():
            filename = f"{pos_dir}/{category_name}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(cat_articles, f, ensure_ascii=False, indent=2)
            print(f"[AUTO-SAVE] {len(cat_articles)} artikler gemt i {filename}")
            pos_total += len(cat_articles)
        
        # Gem index for POS
        pos_index = {
            "main_category": "pos",
            "total_articles": pos_total,
            "categories": {name: len(articles) for name, articles in pos_categories.items()}
        }
        with open(f"{pos_dir}/index.json", "w", encoding="utf-8") as f:
            json.dump(pos_index, f, ensure_ascii=False, indent=2)
        
        total_articles += pos_total
        print(f"[AUTO-SAVE] Totalt {pos_total} POS artikler gemt i {len(pos_categories)} kategorier")
    
    # Gem Webshop kategorier
    if webshop_categories:
        webshop_dir = "Cowis Webshop/categories"
        os.makedirs(webshop_dir, exist_ok=True)
        webshop_total = 0
        
        for category_name, cat_articles in webshop_categories.items():
            filename = f"{webshop_dir}/{category_name}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(cat_articles, f, ensure_ascii=False, indent=2)
            print(f"[AUTO-SAVE] {len(cat_articles)} artikler gemt i {filename}")
            webshop_total += len(cat_articles)
        
        # Gem index for Webshop
        webshop_index = {
            "main_category": "webshop",
            "total_articles": webshop_total,
            "categories": {name: len(articles) for name, articles in webshop_categories.items()}
        }
        with open(f"{webshop_dir}/index.json", "w", encoding="utf-8") as f:
            json.dump(webshop_index, f, ensure_ascii=False, indent=2)
        
        total_articles += webshop_total
        print(f"[AUTO-SAVE] Totalt {webshop_total} Webshop artikler gemt i {len(webshop_categories)} kategorier")
    
    # Gem også en samlet fil (valgfri, for bagudkompatibilitet)
    with open("cowis_data_with_embeddings.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"[AUTO-SAVE] ✅ Totalt {total_articles} artikler gemt i {len(category_articles)} kategorier")

def save_progress():
    """Kald save_category_files i stedet."""
    save_category_files()

def scrape_article(url, category_name):
    """Scraper en enkelt artikel og gemmer den."""
    normalized = normalize_url(url)
    if normalized in visited_urls:
        return
    
    visited_urls.add(normalized)
    print(f"📄 Scraper artikel: {url}")
    
    html = fetch_html(url)
    if not html:
        print(f"   ⚠️ Kunne ikke hente HTML fra {url}")
        return
    
    text = extract_article_text(html)
    if text:
        print(f"   ✓ Tekst ekstraheret ({len(text)} tegn)")
        
        # Find billeder på siden
        image_urls = extract_images(html, url)
        if image_urls:
            print(f"   🖼️  Fundet {len(image_urls)} billed(er)")
        
        embedding = get_embedding(text)
        if embedding:
            print(f"   ✓ Embedding oprettet")
            article_data = {
                "url": url,
                "text": text,
                "embedding": embedding,
                "images": image_urls  # Tilføj billed-URLs
            }
            articles.append(article_data)
            
            # Tilføj til kategori
            if category_name not in category_articles:
                category_articles[category_name] = []
            
            # Sørg for at hovedkategorien er tracked (hvis den ikke allerede er det)
            if category_name not in category_main_map:
                category_main_map[category_name] = get_main_category(url)
            
            category_articles[category_name].append(article_data)
            
            print(f"✅ Gemte artikel: {url}")
            
            # Auto-save hver 5. artikel
            if len(articles) % 5 == 0:
                save_progress()
        else:
            print(f"   ⚠️ Embedding fejlede for {url}")
    else:
        print(f"   ⚠️ Kunne ikke ekstraktere tekst fra {url}")
    
    time.sleep(0.5)

def scrape_category(category_url):
    """Scraper alle artikler fra en kategori-side (inkl. paginering)."""
    normalized = normalize_url(category_url)
    if normalized in visited_urls:
        return
    
    visited_urls.add(normalized)
    category_name = get_category_name(category_url)
    main_category = get_main_category(category_url)
    
    # Gem hovedkategori-mapping
    category_main_map[category_name] = main_category
    
    if category_name not in category_articles:
        category_articles[category_name] = []
    
    print(f"\n📁 Scraper kategori: {category_name} ({main_category.upper()})")
    print(f"   URL: {category_url}")
    
    # Håndter paginering - scrape alle sider
    pages_to_scrape = [category_url]
    visited_pages = set()
    
    while pages_to_scrape:
        page_url = pages_to_scrape.pop(0)
        page_normalized = normalize_url(page_url)
        
        if page_normalized in visited_pages:
            continue
        
        visited_pages.add(page_normalized)
        print(f"\n   📄 Læser side: {page_url}")
        
        html = fetch_html(page_url)
        if not html:
            continue
        
        # Find alle artikel-links på denne side
        article_links = extract_article_links(html, BASE_URL)
        print(f"   🔗 Fundet {len(article_links)} artikler på denne side")
        
        # Scrape hver artikel
        for article_url in article_links:
            scrape_article(article_url, category_name)
        
        # Tjek for paginering (find links til side 2, 3, osv.)
        # Tjek for "Seite X von Y" og find links til næste sider
        soup = BeautifulSoup(html, "html.parser")
        
        # Find pagination links (oftest i samme kategori)
        for a in soup.find_all("a", href=True):
            href = a["href"]
            full_url = urljoin(BASE_URL, href)
            link_normalized = normalize_url(full_url)
            
            # Hvis det er en link til samme kategori (samme base path)
            if (link_normalized.startswith(BASE_URL.rstrip("/")) and 
                "/category/" in link_normalized and
                link_normalized not in visited_pages and
                link_normalized not in pages_to_scrape):
                # Tjek om det ser ud som en pagination link (har side nummer eller lignende)
                text = a.get_text().strip()
                if any(char.isdigit() for char in text) or "→" in text or "⇥" in text:
                    pages_to_scrape.append(full_url)
        
        time.sleep(0.5)

if __name__ == "__main__":
    print(f"🚀 Starter scraping af {len(START_CATEGORIES)} kategorier...\n")
    
    for cat_url in START_CATEGORIES:
        scrape_category(cat_url)
        time.sleep(1)  # Pause mellem kategorier
    
    save_progress()
    print(f"\n✅ Færdig! Gemte i alt {len(articles)} artikler i {len(category_articles)} kategorier.")

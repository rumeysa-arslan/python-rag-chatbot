import os
import chromadb
from dotenv import load_dotenv
from tqdm import tqdm
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# --- Ortam değişkenlerini yükle ---
load_dotenv()

# --- Sabitler ---
CHROMA_DB_PATH = "chroma_db"
import os
os.makedirs(CHROMA_DB_PATH, exist_ok=True)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
COLLECTION_NAME = "python_docs"

# --- Embedding Modelini Hazırla ---
def get_embedding_function():
    if not GEMINI_API_KEY:
        raise ValueError("❌ GEMINI_API_KEY bulunamadı. Lütfen .env dosyasına ekleyin.")
    
    # LangChain tabanlı Google Embedding Model
    embeddings = GoogleGenerativeAIEmbeddings(
        model="text-embedding-004",
        google_api_key=GEMINI_API_KEY
    )
    return embeddings

# --- Kaynak Belgeleri Yükle ---
def load_documents(docs_path="python-3.14-docs-text"):
    documents = []
    ids = []

    if not os.path.exists(docs_path):
        raise FileNotFoundError(f"📁 '{docs_path}' klasörü bulunamadı. Lütfen dokümanları ekleyin.")

    print(f"\n📘 '{docs_path}' klasöründen dokümanlar yükleniyor...\n")

    for i, filename in enumerate(tqdm(os.listdir(docs_path))):
        if not filename.endswith(".txt"):
            continue
        file_path = os.path.join(docs_path, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                documents.append(content)
                ids.append(str(i))
    
    if not documents:
        raise ValueError("⚠ Yüklenecek doküman bulunamadı. Lütfen .txt dosyaları ekle.")
    
    return documents, ids

# --- Vektör DB oluştur ve verileri ekle ---
def build_chroma_db():
    print("🚀 RAG pipeline başlatılıyor...")

    embeddings = get_embedding_function()
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    # Önceki koleksiyon varsa sil
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        print(f"🧹 Eski koleksiyon siliniyor: {COLLECTION_NAME}")
        client.delete_collection(COLLECTION_NAME)

    # Yeni koleksiyon oluştur
    collection = client.create_collection(name=COLLECTION_NAME)

    # Belgeleri yükle
    documents, ids = load_documents("python-3.14-docs-text")

    print(f"🧠 {len(documents)} belge işleniyor ve ChromaDB'ye ekleniyor...")
    vectors = embeddings.embed_documents(documents)

    collection.add(
        ids=ids,
        embeddings=vectors,
        documents=documents
    )

    print("✅ Veritabanı başarıyla oluşturuldu!")
    print(f"📂 Klasör: {CHROMA_DB_PATH}")
    print(f"📚 Koleksiyon: {COLLECTION_NAME}")

# --- Ana Çalıştırma ---
if __name__ == "_main_":
    try:
        build_chroma_db()
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
import streamlit as st
import os
import chromadb
from google import genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings as GGClientEmbedings
from chromadb.api.models.Collection import Collection

if "GEMINI_API_KEY" not in st.secrets:
    st.error("HATA: Uygulamayı çalıştırmak için GEMINI_API_KEY gizli anahtarı bulunamadı. Lütfen Streamlit Cloud ayarlarına ekleyin.")
    st.stop()
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# --- Sabitler ve Ayarlar ---
CHROMA_DB_PATH = "chroma_db"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") 
LLM_MODEL = "gemini-2.5-flash"

# --- RAG Prompt ---
RAG_PROMPT_TEMPLATE = """
Sen, Python programlama dili hakkında uzman bir eğitmen ve yardımcısın. 
Kullanıcının sorularını yalnızca aşağıdaki BAĞLAM'da bulunan dokümanlardan aldığın bilgilerle yanıtla.
Eğer bağlamda soruya cevap bulamıyorsan, "Bu soruya mevcut Python dokümanlarımda yanıt bulamıyorum." de.

BAĞLAM: {context}

SORU: {question}
"""

# --- Başlangıç Fonksiyonu (Vektör DB'yi Güvenli Yükleme) ---
@st.cache_resource 
def setup_rag_pipeline() -> Collection | None:
    # API Key kontrolünü yukarıya taşıdık. Burada tekrar kontrol etmeye gerek yok.

    try:
        # 1. Vektörleştirme Modeli
        embedding_function = GGClientEmbedings(
            model="text-embedding-004"
        )
        
        # 2. Vektör Veritabanını Yükleme (Koleksiyonun Var Olup Olmadığını Kontrol Etmek Gerekir)
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

        # Koleksiyonun varlığını kontrol etmek için list_collections kullanılır.
        existing_collections = client.list_collections()
        if "python_docs" not in [c.name for c in existing_collections]:
            # KRİTİK DÜZELTME: Koleksiyon yoksa hata fırlatmak yerine uyarı veriyoruz.
            # Bu, uygulamanın çökmesini engeller.
            st.warning("""
            🚨 UYARI: 'python_docs' RAG koleksiyonu bulunamadı. 
            Lütfen verileri yükleme (embed etme) betiğini (örn. 'rag_pipeline.py' veya 'setup.py') Streamlit ortamında ayrıca çalıştırdığınızdan emin olun. 
            Bu uygulama RAG olmadan çalışamayacaktır.
            """)
            return None
        
        # Koleksiyon var, güvenle alabiliriz
        collection = client.get_collection(
            name="python_docs",
            embedding_function=embedding_function
        )

        # Gemini LLM'i configure et
        genai.configure(api_key=GEMINI_API_KEY)
        return collection
        
    except Exception as e:
        # Diğer olası hataları (dosya erişimi vb.) yakalarız
        st.error(f"RAG bileşenleri yüklenirken beklenmedik bir hata oluştu: {e}")
        return None

# --- Chat Fonksiyonu ---
def generate_response(collection, prompt: str):
    # 1. Geri Çekme (Retrieval)
    results = collection.query(
        query_texts=[prompt],
        n_results=3
    )
    
    # 2. Bağlamı (Context) Birleştirme
    context = "\n---\n".join([doc for docs in results.get('documents', [[]]) for doc in docs])
    
    # 3. Prompt'u Hazırlama
    final_prompt = RAG_PROMPT_TEMPLATE.format(context=context, question=prompt)
    
    # 4. Üretme (Generation)
    response = genai.GenerativeModel(model_name=LLM_MODEL).generate_content(
        contents=final_prompt,
        config=genai.types.GenerateContentConfig(
            temperature=0.1
        )
    )
    return response.text


# --- Streamlit Arayüzü ---

st.set_page_config(page_title="Akbank Python RAG Chatbot")
st.title("🐍 Python Öğrenme RAG Chatbotu (Temel)")

# Güvenli yükleme (Hata durumunda None döner)
collection = setup_rag_pipeline()

if collection:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Python ile ilgili sorunuz nedir?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Yanıt aranıyor..."):
                try:
                    response = generate_response(collection, prompt) 
                    st.markdown(response)
                except Exception as e:
                    response = f"Üzgünüm, yanıt oluşturulurken bir hata oluştu: {e}"
                    st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
else:
    # Koleksiyon bulunamadığında chat arayüzünü gösterme
    st.info("Lütfen RAG veritabanını yükledikten sonra sayfayı yenileyin.")
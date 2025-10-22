import streamlit as st
import os
import chromadb
from google import genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings as GGClientEmbedings
from chromadb.api.models.Collection import Collection


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

# --- Başlangıç Fonksiyonu (Vektör DB'yi Yükleme) ---
@st.cache_resource 
def setup_rag_pipeline() -> Collection:
    if not GEMINI_API_KEY:
        st.error("HATA: GEMINI_API_KEY ortam değişkeni bulunamadı.")
        return None

    try:
        # 1. Vektörleştirme Modeli (Google'ın kendi kütüphanesi)
        embedding_function = GGClientEmbedings(
             
            model="text-embedding-004"
        )
        
        # 2. Vektör Veritabanını Yükleme
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        collection = client.get_collection(
            name="python_docs",
            embedding_function=embedding_function
        )
        
        # Eğer collection boşsa (veri yüklenmediyse), hata ver
        if collection.count() == 0:
            st.warning("Veritabanı boş görünüyor. Lütfen 'rag_pipeline.py' dosyasını çalıştırdığınızdan emin olun.")

        # Gemini LLM'i configure et
        genai.configure(api_key=GEMINI_API_KEY)
        return collection
        
    except Exception as e:
        st.error(f"RAG bileşenleri yüklenirken KRİTİK HATA oluştu: {e}")
        return None

# --- Chat Fonksiyonu ---
def generate_response(collection, prompt: str):
    # 1. Geri Çekme (Retrieval)
    results = collection.query(
        query_texts=[prompt],
        n_results=3
    )
    
    # 2. Bağlamı (Context) Birleştirme
    context = "\n---\n".join([doc for docs in results['documents'] for doc in docs])
    
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
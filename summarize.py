from flask import Flask, request, render_template, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import nltk

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Pastikan nltk sudah siap
nltk.download('punkt')
nltk.download('stopwords')

# Fungsi ringkasan dengan pendekatan Information Retrieval
def summarize_ir(content, num_sentences=7, proportion=0.5, language='english'):
    """
    Merangkum teks menggunakan pendekatan berbasis IR (TF-IDF dan cosine similarity).
    
    Args:
        content (str): Teks panjang yang akan dirangkum.
        num_sentences (int): Jumlah kalimat tetap untuk ringkasan (opsional).
        proportion (float): Proporsi kalimat yang ingin diambil (default: 20% dari total kalimat).
        language (str): Bahasa teks (default: 'english').
    
    Returns:
        str: Ringkasan teks.
    """
    # Tokenisasi teks menjadi kalimat
    sentences = sent_tokenize(content, language=language)
    total_sentences = len(sentences)
    
    # Jika teks terlalu pendek, langsung dikembalikan
    if total_sentences < 2:
        return content
    
    # Tentukan jumlah kalimat ringkasan berdasarkan parameter
    if num_sentences is None:
        num_sentences = max(1, int(total_sentences * proportion))

    # Menggunakan stop words berdasarkan bahasa
    stop_words = stopwords.words(language)

    # Menghitung bobot TF-IDF untuk setiap kalimat
    vectorizer = TfidfVectorizer(stop_words=stop_words)
    tfidf_matrix = vectorizer.fit_transform(sentences)
    
    # Menghitung similarity matrix menggunakan cosine similarity
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    # Skor setiap kalimat berdasarkan kemiripan kosinus
    sentence_scores = similarity_matrix.sum(axis=1)
    
    # Mengurutkan kalimat berdasarkan skor (dari tinggi ke rendah)
    ranked_indices = sentence_scores.argsort()[::-1]
    ranked_sentences = [sentences[i] for i in ranked_indices]
    
    # Pilih kalimat dengan skor tertinggi sesuai num_sentences
    summary = ' '.join(ranked_sentences[:num_sentences])
    return summary

# Route untuk halaman utama
@app.route('/')
def home():
    return render_template('index.html')

# Route untuk API ringkasan teks
@app.route('/summarize', methods=['POST'])
def summarize_text():
    data = request.get_json()  # Ambil JSON dari body request
    text = data.get('text', '')  # Pastikan ada teks
    if not text:
        return jsonify({'error': 'Teks tidak ditemukan!'}), 400
    
    # Proses ringkasan menggunakan summarize_ir
    summary = summarize_ir(text, proportion=0.5, language='indonesian')
    return jsonify({'summary': summary})

# Route untuk upload file
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded!'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file!'}), 400

    # Baca file teks atau PDF
    if file.filename.endswith('.txt'):
        content = file.read().decode('utf-8')
    elif file.filename.endswith('.pdf'):
        from PyPDF2 import PdfReader
        pdf_reader = PdfReader(file)
        content = ''
        for page in pdf_reader.pages:
            content += page.extract_text()
    else:
        return jsonify({'error': 'Unsupported file format! Only .txt and .pdf allowed.'}), 400

    # Proses ringkasan menggunakan summarize_ir
    summary = summarize_ir(content, proportion=0.5, language='indonesian')
    return jsonify({'summary': summary})

if __name__ == '__main__':
    app.run(debug=True)

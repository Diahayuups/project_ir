from flask import Flask, request, render_template, jsonify
from PyPDF2 import PdfReader
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Fungsi ringkasan
def summarize(content):
    sentences = sent_tokenize(content)
    if len(sentences) < 2:
        return content  # Return teks jika terlalu pendek
    
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(sentences)
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Pilih kalimat dengan skor tertinggi
    scores = similarity_matrix.sum(axis=1)
    ranked_sentences = [sentences[i] for i in scores.argsort()[::-1]]
    summary = ' '.join(ranked_sentences[:3])  # Ambil 3 kalimat teratas
    return summary

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize_text():
    data = request.get_json()  # Ambil JSON dari body request
    text = data.get('text', '')  # Pastikan ada teks
    summary = summarize(text)
    return jsonify({'summary': summary})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded!'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file!'}), 400

    if file.filename.endswith('.txt'):
        content = file.read().decode('utf-8')
    elif file.filename.endswith('.pdf'):
        pdf_reader = PdfReader(file)
        content = ''
        for page in pdf_reader.pages:
            content += page.extract_text()
    else:
        return jsonify({'error': 'Unsupported file format! Only .txt and .pdf allowed.'}), 400

    summary = summarize(content)
    return jsonify({'summary': summary})

if __name__ == '__main__':
    app.run(debug=True)

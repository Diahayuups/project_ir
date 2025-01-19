// Form teks
document.getElementById('textForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const text = document.getElementById('textInput').value;
    if (!text) {
        alert('Please enter some text to summarize');
        return;
    }

    try {
        const response = await fetch('/summarize', { // Ganti endpoint
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text }) // Kirim JSON
        });

        const data = await response.json();
        document.getElementById('resultArea').value = data.summary;
    } catch (error) {
        console.error('Error:', error);
        alert('Error processing text. Please try again.');
    }
});

// Form file
document.getElementById('fileForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const fileInput = document.getElementById('fileInput');
    if (!fileInput.files[0]) {
        alert('Please select a file to upload');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch('/upload', { // Ganti endpoint
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        document.getElementById('resultArea').value = data.summary;
    } catch (error) {
        console.error('Error:', error);
        alert('Error processing file. Please try again.');
    }
});

document.getElementById('fileInput').addEventListener('change', function (e) {
    console.log('File selected:', e.target.files[0]);
    const fileName = e.target.files[0] ? e.target.files[0].name : 'Name Of File';
    document.getElementById('fileName').textContent = fileName;
});
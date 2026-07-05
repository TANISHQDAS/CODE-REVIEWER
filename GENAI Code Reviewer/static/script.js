// NEOBRUTALIST CODE REVIEWER - Simple & Raw
const codeEditor = document.getElementById('codeEditor');

// REVIEW button
document.getElementById('reviewBtn').onclick = () => {
    const code = codeEditor.value.trim();
    if (!code) {
        alert('ENTER SOME CODE FIRST');
        return;
    }
    submitCode(code);
};

// UPLOAD button
document.getElementById('upload').onclick = () => {
    document.getElementById('fileInput').click();
};

document.getElementById('fileInput').onchange = (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
            codeEditor.value = event.target.result;
        };
        reader.readAsText(file);
    }
};

// CLEAR button
document.getElementById('clear').onclick = () => {
    codeEditor.value = '';
    document.getElementById('result').innerHTML = '';
    document.getElementById('loading').classList.remove('hide');
    document.getElementById('result').classList.remove('show');
};

// COPY button
document.getElementById('copy').onclick = () => {
    const text = document.getElementById('result').innerText;
    navigator.clipboard.writeText(text).then(() => {
        alert('✓ COPIED');
    });
};

// DOWNLOAD button
document.getElementById('download').onclick = () => {
    const text = document.getElementById('result').innerText;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'review.txt';
    a.click();
};

// THEME toggle
document.getElementById('theme').onclick = () => {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    document.getElementById('theme').textContent = isDark ? 'LIGHT' : 'DARK';
    localStorage.setItem('dark-mode', isDark ? '1' : '');
};

// Load dark mode preference
window.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('dark-mode')) {
        document.body.classList.add('dark-mode');
        document.getElementById('theme').textContent = 'LIGHT';
    }
    codeEditor.focus();
});

// Submit code via FETCH
function submitCode(code) {
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');
    
    loading.classList.remove('hide');
    result.classList.remove('show');
    
    fetch('/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({ code: code })
    })
    .then(response => response.text())
    .then(html => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const resultDiv = doc.getElementById('result');
        
        if (resultDiv) {
            result.innerHTML = resultDiv.innerHTML;
        }
        
        loading.classList.add('hide');
        result.classList.add('show');
    })
    .catch(error => {
        console.error('Error:', error);
        result.innerHTML = '<p>ERROR: Could not get review. Try again.</p>';
        loading.classList.add('hide');
        result.classList.add('show');
    });
}
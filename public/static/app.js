document.addEventListener('DOMContentLoaded', () => {
    const mediaModal = document.getElementById('media-modal');
    const fileInput = document.getElementById('file-input');
    
    // Media selection handler
    document.getElementById('add-media').addEventListener('click', () => {
        mediaModal.style.display = 'block';
    });

    // File upload handling
    document.getElementById('upload-btn').addEventListener('click', () => {
        fileInput.click();
    });

    // API communication
    document.getElementById('send-btn').addEventListener('click', async () => {
        const formData = new FormData();
        formData.append('prompt', document.getElementById('prompt').value);
        
        // Add your file/URL handling logic here
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        // Add response handling
    });
});
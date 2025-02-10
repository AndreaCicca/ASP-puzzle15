document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('puzzleForm');
    const loading = document.querySelector('.loading');
    const resultGif = document.getElementById('resultGif');
    const previewContainer = document.getElementById('preview-container');
    let previewTimeout;

    // Live preview function
    const updatePreview = () => {
        const holdsContent = document.getElementById('holds').value;

        // Clear previous preview request if any
        if (previewTimeout) {
            clearTimeout(previewTimeout);
        }

        // Show preview after 500ms of user stopping typing
        previewTimeout = setTimeout(async () => {
            if (holdsContent.trim() !== '') {
                const formData = new FormData();
                formData.append('holds', holdsContent);

                try {
                    const response = await fetch('/generate', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        throw new Error(await response.text());
                    }
                    
                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    resultGif.src = url;
                    resultGif.style.display = 'block';
                } catch (error) {
                    console.error('Preview error:', error);
                }
            }
        }, 500);
    };

    // Add event listener for live preview
    document.getElementById('holds').addEventListener('input', updatePreview);

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        
        // Show loading state
        loading.style.display = 'block';
        resultGif.style.display = 'none';
        
        try {
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(await response.text());
            }
            
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            resultGif.src = url;
            resultGif.style.display = 'block';
            
            // Smooth scroll to result
            resultGif.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } catch (error) {
            alert('Errore: ' + error.message);
        } finally {
            loading.style.display = 'none';
        }
    });
});
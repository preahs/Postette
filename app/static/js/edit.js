document.addEventListener('DOMContentLoaded', function() {
    // Handle image removal
    document.querySelectorAll('.remove-image-preview').forEach(button => {
        button.addEventListener('click', function() {
            const container = this.closest('.image-preview-item');
            const filename = container.dataset.filename;
            
            if (this.dataset.action === 'remove-existing') {
                // Remove the hidden input for existing image
                const input = container.querySelector('input[name="existing_images"]');
                if (input) {
                    input.remove();
                }
            }
            
            container.remove();
        });
    });

    // Handle video removal
    document.querySelectorAll('.remove-video-preview').forEach(button => {
        button.addEventListener('click', function() {
            const container = this.closest('.video-preview-item');
            const filename = container.dataset.filename;
            
            if (this.dataset.action === 'remove-existing') {
                // Remove the hidden input for existing video
                const input = container.querySelector('input[name="existing_videos"]');
                if (input) {
                    input.remove();
                }
            }
            
            container.remove();
        });
    });

    // Lightbox modal for viewing all images in archived post or homepage
    const modal = document.getElementById('imageLightboxModal');
    const closeBtn = document.getElementById('closeLightbox');
    const imagesContainer = document.getElementById('lightboxImagesContainer');

    if (!modal || !closeBtn || !imagesContainer) return;

    // Delegate event for dynamically created buttons
    document.body.addEventListener('click', function(e) {
        if (e.target.classList.contains('view-all-photos-btn')) {
            const images = e.target.getAttribute('data-images').split(',');
            imagesContainer.innerHTML = '';
            images.forEach(filename => {
                const img = document.createElement('img');
                img.src = `/static/uploads/${filename.trim()}`;
                img.alt = 'Post image';
                img.style.maxWidth = '300px';
                img.style.maxHeight = '300px';
                img.style.margin = '8px';
                imagesContainer.appendChild(img);
            });
            modal.style.display = 'flex';
        }
    });

    closeBtn.addEventListener('click', function() {
        modal.style.display = 'none';
        imagesContainer.innerHTML = '';
    });

    // Close modal when clicking outside the image area
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
            imagesContainer.innerHTML = '';
        }
    });
}); 
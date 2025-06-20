document.addEventListener('DOMContentLoaded', function() {
    // Handles removal of EXISTING images
    const removeExistingImageButtons = document.querySelectorAll('.image-preview-item.existing-image-item .remove-image-preview[data-action="remove-existing"]');
    
    removeExistingImageButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const imagePreviewItem = this.closest('.image-preview-item');
            const filename = imagePreviewItem.dataset.filename;
            const postId = window.location.pathname.split('/')[2];
            
            try {
                const response = await fetch(`/remove-image/${postId}/${filename}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        // Add CSRF token if you have it in your forms
                        // 'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
                    }
                });
                
                if (response.ok) {
                    imagePreviewItem.remove(); // Remove the image element from the DOM
                } else {
                    console.error('Failed to remove image on server:', response.statusText);
                    alert('Failed to remove image. Please try again.');
                }
            } catch (error) {
                console.error('Error removing image:', error);
                alert('An error occurred while removing the image.');
            }
        });
    });

    // Handles removal of EXISTING videos
    const removeExistingVideoButtons = document.querySelectorAll('.video-preview-item.existing-video-item .remove-video-preview[data-action="remove-existing"]');
    
    removeExistingVideoButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const videoPreviewItem = this.closest('.video-preview-item');
            const filename = videoPreviewItem.dataset.filename;
            const postId = window.location.pathname.split('/')[2];
            
            try {
                const response = await fetch(`/remove-video/${postId}/${filename}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                
                if (response.ok) {
                    videoPreviewItem.remove();
                } else {
                    console.error('Failed to remove video on server:', response.statusText);
                    alert('Failed to remove video. Please try again.');
                }
            } catch (error) {
                console.error('Error removing video:', error);
                alert('An error occurred while removing the video.');
            }
        });
    });
}); 
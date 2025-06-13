document.addEventListener('DOMContentLoaded', function() {
    const removeButtons = document.querySelectorAll('.remove-image');
    
    removeButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const filename = this.dataset.filename;
            const postId = window.location.pathname.split('/')[2];
            
            try {
                const response = await fetch(`/remove-image/${postId}/${filename}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                
                if (response.ok) {
                    // Remove the image element from the DOM
                    const imageItem = this.closest('.image-item');
                    imageItem.remove();
                    
                    // If no images left, remove the "Current images" section
                    const imageList = document.querySelector('.image-list');
                    if (imageList && !imageList.children.length) {
                        const currentImages = document.querySelector('.current-images');
                        if (currentImages) {
                            currentImages.remove();
                        }
                    }
                }
            } catch (error) {
                console.error('Error removing image:', error);
            }
        });
    });
}); 
document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const imagePreviewContainer = document.getElementById('image-preview-container');

    const MAX_TOTAL_IMAGE_SIZE_MB = 15; // Max 15 MB total for images (adjusted for base64 encoding)
    const MAX_TOTAL_IMAGE_SIZE_BYTES = MAX_TOTAL_IMAGE_SIZE_MB * 1024 * 1024;

    let filesToUpload = new DataTransfer();
    let currentTotalSize = 0;

    // Initialize currentTotalSize with existing images' sizes on edit page
    document.querySelectorAll('.image-preview-item.existing-image-item').forEach(item => {
        const size = parseInt(item.dataset.size, 10);
        if (!isNaN(size)) {
            currentTotalSize += size;
        }
    });

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop zone when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('highlight'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('highlight'), false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);

    // Handle click on drop zone to open file input
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    // Handle file selection via input
    fileInput.addEventListener('change', handleFileInputChange);

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    function handleFileInputChange(e) {
        const files = e.target.files;
        handleFiles(files);
    }

    function handleFiles(files) {
        let filesRejectedCount = 0;
        let filesToProcess = Array.from(files); // Copy to iterate safely

        for (let i = 0; i < filesToProcess.length; i++) {
            const file = filesToProcess[i];
            if (file.type.startsWith('image/')) {
                if (currentTotalSize + file.size <= MAX_TOTAL_IMAGE_SIZE_BYTES) {
                    filesToUpload.items.add(file);
                    previewFile(file, file.size);
                    currentTotalSize += file.size;
                } else {
                    filesRejectedCount++;
                }
            }
        }

        // Update the actual file input with the combined list of files
        fileInput.files = filesToUpload.files;

        if (filesRejectedCount > 0) {
            alert(`Could not attach ${filesRejectedCount} image(s) due to the total size limit of ${MAX_TOTAL_IMAGE_SIZE_MB}MB.`);
        }
    }

    function previewFile(file, size) {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onloadend = function() {
            const previewWrapper = document.createElement('div');
            previewWrapper.classList.add('image-preview-item');
            previewWrapper.dataset.size = size; // Store size for new images

            const img = document.createElement('img');
            img.src = reader.result;
            img.alt = file.name;

            const removeBtn = document.createElement('button');
            removeBtn.classList.add('remove-image-preview');
            removeBtn.innerHTML = '&times;'; // 'x' icon
            removeBtn.addEventListener('click', () => {
                removeFile(file, previewWrapper);
            });

            previewWrapper.appendChild(img);
            previewWrapper.appendChild(removeBtn);
            imagePreviewContainer.appendChild(previewWrapper);
        }
    }

    function removeFile(fileToRemove, previewWrapper) {
        const removedFileSize = parseInt(previewWrapper.dataset.size, 10);
        if (!isNaN(removedFileSize)) {
            currentTotalSize -= removedFileSize;
        }

        // If removing a newly added file
        let newFilesDt = new DataTransfer();
        Array.from(filesToUpload.files).forEach(file => {
            if (file !== fileToRemove) {
                newFilesDt.items.add(file);
            }
        });
        filesToUpload = newFilesDt;
        fileInput.files = filesToUpload.files;

        previewWrapper.remove();
    }

    // Handle removal of existing images that were pre-rendered
    imagePreviewContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove-image-preview') && e.target.dataset.action === 'remove-existing') {
            const imagePreviewItem = e.target.closest('.image-preview-item.existing-image-item');
            if (imagePreviewItem) {
                const removedFileSize = parseInt(imagePreviewItem.dataset.size, 10);
                if (!isNaN(removedFileSize)) {
                    currentTotalSize -= removedFileSize;
                }
                // Do not remove from filesToUpload as it's an existing file
                // The server-side will handle actual deletion via edit.js logic

                imagePreviewItem.remove();
            }
        }
    });
}); 
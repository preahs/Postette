document.addEventListener('DOMContentLoaded', () => {
    const imageDropZone = document.getElementById('image-drop-zone');
    const videoDropZone = document.getElementById('video-drop-zone');
    const imageFileInput = document.getElementById('image-file-input');
    const videoFileInput = document.getElementById('video-file-input');
    const imagePreviewContainer = document.getElementById('image-preview-container');
    const videoPreviewContainer = document.getElementById('video-preview-container');

    const MAX_TOTAL_IMAGE_SIZE_MB = 15;
    const MAX_TOTAL_IMAGE_SIZE_BYTES = MAX_TOTAL_IMAGE_SIZE_MB * 1024 * 1024;
    const MAX_TOTAL_VIDEO_SIZE_MB = 15;
    const MAX_TOTAL_VIDEO_SIZE_BYTES = MAX_TOTAL_VIDEO_SIZE_MB * 1024 * 1024;

    let imageFilesToUpload = new DataTransfer();
    let videoFilesToUpload = new DataTransfer();
    let currentTotalImageSize = 0;
    let currentTotalVideoSize = 0;

    // Initialize currentTotalSize with existing media's sizes on edit page
    document.querySelectorAll('.image-preview-item.existing-image-item').forEach(item => {
        const size = parseInt(item.dataset.size, 10);
        if (!isNaN(size)) {
            currentTotalImageSize += size;
        }
    });

    document.querySelectorAll('.video-preview-item.existing-video-item').forEach(item => {
        const size = parseInt(item.dataset.size, 10);
        if (!isNaN(size)) {
            currentTotalVideoSize += size;
        }
    });

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        [imageDropZone, videoDropZone].forEach(zone => {
            if (zone) {
                zone.addEventListener(eventName, preventDefaults, false);
                document.body.addEventListener(eventName, preventDefaults, false);
            }
        });
    });

    // Highlight drop zone when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        [imageDropZone, videoDropZone].forEach(zone => {
            if (zone) {
                zone.addEventListener(eventName, () => zone.classList.add('highlight'), false);
            }
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        [imageDropZone, videoDropZone].forEach(zone => {
            if (zone) {
                zone.addEventListener(eventName, () => zone.classList.remove('highlight'), false);
            }
        });
    });

    // Handle dropped files
    if (imageDropZone) {
        imageDropZone.addEventListener('drop', handleImageDrop, false);
        imageDropZone.addEventListener('click', () => imageFileInput.click());
    }

    if (videoDropZone) {
        videoDropZone.addEventListener('drop', handleVideoDrop, false);
        videoDropZone.addEventListener('click', () => videoFileInput.click());
    }

    // Handle file selection via input
    if (imageFileInput) {
        imageFileInput.addEventListener('change', handleImageFileInputChange);
    }

    if (videoFileInput) {
        videoFileInput.addEventListener('change', handleVideoFileInputChange);
    }

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function handleImageDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleImageFiles(files);
    }

    function handleVideoDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleVideoFiles(files);
    }

    function handleImageFileInputChange(e) {
        const files = e.target.files;
        handleImageFiles(files);
    }

    function handleVideoFileInputChange(e) {
        const files = e.target.files;
        handleVideoFiles(files);
    }

    function handleImageFiles(files) {
        let filesRejectedCount = 0;
        let filesToProcess = Array.from(files);

        for (let i = 0; i < filesToProcess.length; i++) {
            const file = filesToProcess[i];
            if (file.type.startsWith('image/')) {
                if (currentTotalImageSize + file.size <= MAX_TOTAL_IMAGE_SIZE_BYTES) {
                    imageFilesToUpload.items.add(file);
                    previewImageFile(file, file.size);
                    currentTotalImageSize += file.size;
                } else {
                    filesRejectedCount++;
                }
            }
        }

        imageFileInput.files = imageFilesToUpload.files;

        if (filesRejectedCount > 0) {
            alert(`Could not attach ${filesRejectedCount} image(s) due to the total size limit of ${MAX_TOTAL_IMAGE_SIZE_MB}MB.`);
        }
    }

    function handleVideoFiles(files) {
        let filesRejectedCount = 0;
        let filesToProcess = Array.from(files);

        for (let i = 0; i < filesToProcess.length; i++) {
            const file = filesToProcess[i];
            if (file.type.startsWith('video/')) {
                if (currentTotalVideoSize + file.size <= MAX_TOTAL_VIDEO_SIZE_BYTES) {
                    videoFilesToUpload.items.add(file);
                    previewVideoFile(file, file.size);
                    currentTotalVideoSize += file.size;
                } else {
                    filesRejectedCount++;
                }
            }
        }

        videoFileInput.files = videoFilesToUpload.files;

        if (filesRejectedCount > 0) {
            alert(`Could not attach ${filesRejectedCount} video(s) due to the total size limit of ${MAX_TOTAL_VIDEO_SIZE_MB}MB.`);
        }
    }

    function previewImageFile(file, size) {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onloadend = function() {
            const previewWrapper = document.createElement('div');
            previewWrapper.classList.add('image-preview-item');
            previewWrapper.dataset.size = size;

            const img = document.createElement('img');
            img.src = reader.result;
            img.alt = file.name;

            const removeBtn = document.createElement('button');
            removeBtn.classList.add('remove-image-preview');
            removeBtn.innerHTML = '&times;';
            removeBtn.addEventListener('click', () => {
                removeImageFile(file, previewWrapper);
            });

            previewWrapper.appendChild(img);
            previewWrapper.appendChild(removeBtn);
            imagePreviewContainer.appendChild(previewWrapper);
        }
    }

    function previewVideoFile(file, size) {
        const previewWrapper = document.createElement('div');
        previewWrapper.classList.add('video-preview-item');
        previewWrapper.dataset.size = size;

        const video = document.createElement('video');
        video.src = URL.createObjectURL(file);
        video.controls = true;
        video.className = 'video-thumbnail';

        const removeBtn = document.createElement('button');
        removeBtn.classList.add('remove-video-preview');
        removeBtn.innerHTML = '&times;';
        removeBtn.addEventListener('click', () => {
            removeVideoFile(file, previewWrapper);
        });

        previewWrapper.appendChild(video);
        previewWrapper.appendChild(removeBtn);
        videoPreviewContainer.appendChild(previewWrapper);
    }

    function removeImageFile(fileToRemove, previewWrapper) {
        const removedFileSize = parseInt(previewWrapper.dataset.size, 10);
        if (!isNaN(removedFileSize)) {
            currentTotalImageSize -= removedFileSize;
        }

        let newFilesDt = new DataTransfer();
        Array.from(imageFilesToUpload.files).forEach(file => {
            if (file !== fileToRemove) {
                newFilesDt.items.add(file);
            }
        });
        imageFilesToUpload = newFilesDt;
        imageFileInput.files = imageFilesToUpload.files;

        previewWrapper.remove();
    }

    function removeVideoFile(fileToRemove, previewWrapper) {
        const removedFileSize = parseInt(previewWrapper.dataset.size, 10);
        if (!isNaN(removedFileSize)) {
            currentTotalVideoSize -= removedFileSize;
        }

        let newFilesDt = new DataTransfer();
        Array.from(videoFilesToUpload.files).forEach(file => {
            if (file !== fileToRemove) {
                newFilesDt.items.add(file);
            }
        });
        videoFilesToUpload = newFilesDt;
        videoFileInput.files = videoFilesToUpload.files;

        previewWrapper.remove();
    }

    // Handle removal of existing media that were pre-rendered
    if (imagePreviewContainer) {
        imagePreviewContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-image-preview') && e.target.dataset.action === 'remove-existing') {
                const imagePreviewItem = e.target.closest('.image-preview-item.existing-image-item');
                if (imagePreviewItem) {
                    const removedFileSize = parseInt(imagePreviewItem.dataset.size, 10);
                    if (!isNaN(removedFileSize)) {
                        currentTotalImageSize -= removedFileSize;
                    }
                    imagePreviewItem.remove();
                }
            }
        });
    }

    if (videoPreviewContainer) {
        videoPreviewContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-video-preview') && e.target.dataset.action === 'remove-existing') {
                const videoPreviewItem = e.target.closest('.video-preview-item.existing-video-item');
                if (videoPreviewItem) {
                    const removedFileSize = parseInt(videoPreviewItem.dataset.size, 10);
                    if (!isNaN(removedFileSize)) {
                        currentTotalVideoSize -= removedFileSize;
                    }
                    videoPreviewItem.remove();
                }
            }
        });
    }
}); 
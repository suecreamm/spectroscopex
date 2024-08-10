export function initializeTransform(fileUploadHandler) {
    console.log('Initializing Transform module');

    const transformTab = document.querySelector('.tab[data-content="transform"]');
    const transformImage = document.getElementById('transformImage');
    const flipUdBtn = document.getElementById('flipUdBtn');
    const flipLrBtn = document.getElementById('flipLrBtn');
    const rotateCcw90Btn = document.getElementById('rotateCcw90Btn');
    const rotateCw90Btn = document.getElementById('rotateCw90Btn');
    const resetBtn = document.getElementById('resetBtn');
    
    if (!transformTab || !transformImage || !flipUdBtn || !flipLrBtn || !rotateCcw90Btn || !rotateCw90Btn || !resetBtn) {
        console.error('One or more required elements for transform not found');
        return;
    }

    const updateTransformImage = (imageData) => {
        console.log('Updating transform image');
        if (typeof imageData === 'string') {
            if (imageData.startsWith('data:image')) {
                transformImage.src = imageData;
            } else {
                transformImage.src = `data:image/png;base64,${imageData}`;
            }
            transformImage.style.display = "block";
        } else {
            console.error('Invalid image data:', imageData);
        }
    };

    // FileUploadHandler에 updateTransformImage 함수 설정
    fileUploadHandler.setUpdateTransformImage(updateTransformImage);

    transformTab.addEventListener('click', loadTransformedImage);

    flipUdBtn.addEventListener('click', () => sendTransformRequest('flip_ud'));
    flipLrBtn.addEventListener('click', () => sendTransformRequest('flip_lr'));
    rotateCcw90Btn.addEventListener('click', () => sendTransformRequest('rotate_ccw90'));
    rotateCw90Btn.addEventListener('click', () => sendTransformRequest('rotate_cw90'));
    resetBtn.addEventListener('click', handleReset);

    function loadTransformedImage() {
        console.log('Loading transformed image');
        if (transformImage.src && transformImage.src !== window.location.href) {
            transformImage.style.display = "block";
        } else {
            console.log('No transformed image data available yet');
        }
    }

    async function sendTransformRequest(action) {
        console.log(`Sending transform request: ${action}`);
        fileUploadHandler.updateUploadMessage('Transforming image...');
        try {
            const response = await fileUploadHandler.transformImage(action);
            console.log('Transform response:', response);
            if (response.success && response.image) {
                updateTransformImage(response.image);
                fileUploadHandler.updateUploadMessage('Image transformed successfully.');
            } else {
                throw new Error(response.error || 'Unknown error occurred');
            }
        } catch (error) {
            console.error('Transform failed:', error);
            fileUploadHandler.updateUploadMessage(`Transform failed: ${error.message}`);
        }
    }

    function handleReset() {
        console.log('Resetting to initial state');
        fileUploadHandler.resetToInitialState();
    }

    return {
        updateTransformImage
    };
}
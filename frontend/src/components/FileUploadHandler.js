import { showModalMessage } from '../../assets/js/modalMessage.js';
import { showLoadingSpinner, hideLoadingSpinner, disableButtons, enableButtons } from '../../assets/js/uiHelpers.js';

export function initializeFileUploadHandler() {
    const elements = {
        fileInput: document.getElementById('fileInput'),
        previewImage: document.getElementById('previewImage'),
        viewAllBtn: document.getElementById('viewAllBtn'),
        previewTab: document.querySelector('.tab[data-content="preview"]'),
        xProfileTab: document.querySelector('.tab[data-content="x_profile"]'),
        yProfileTab: document.querySelector('.tab[data-content="y_profile"]'),
        uploadMessage: document.getElementById('uploadMessage'),
        xProfilePlot: document.getElementById('x_profile_plot'),
        yProfilePlot: document.getElementById('y_profile_plot'),
        saveImageXProfileBtn: document.getElementById('saveImageXProfileBtn'),
        saveImageYProfileBtn: document.getElementById('saveImageYProfileBtn'),
        exportCSVXProfileBtn: document.getElementById('exportCSVXProfileBtn'),
        exportCSVYProfileBtn: document.getElementById('exportCSVYProfileBtn'),
        exportCSVBtn: document.getElementById('exportCSVBtn'),
        savePreviewBtn: document.getElementById('savePreviewBtn'),
        blurBtn: document.getElementById('blurBtn'),
        sharpenBtn: document.getElementById('sharpenBtn'),
        exportCSVBtn: document.getElementById('exportCSVBtn'),
        qEnergyLossCheckbox: document.getElementById('q-energyloss'),
        flipUdBtn: document.getElementById('flipUdBtn'),
        flipLrBtn: document.getElementById('flipLrBtn'),
        rotateCcw90Btn: document.getElementById('rotateCcw90Btn'),
        rotateCw90Btn: document.getElementById('rotateCw90Btn'),
        resetBtn: document.getElementById('resetBtn')
    };

    let lastUploadedData = null;
    let initialUploadedData = null;
    let isQEnergyLossEnabled = false;
    let qConversionPerformed = false;

    if (Object.values(elements).some(element => !element)) {
        console.error('One or more required elements not found');
        return;
    }

    function updateUploadMessage(message) {
        if (elements.uploadMessage) {
            elements.uploadMessage.textContent = message;
        } else {
            console.error('Upload message element not found');
        }
    }

    async function handleQEnergyLossChange() {
        const wasQEnergyLossEnabled = isQEnergyLossEnabled;
        isQEnergyLossEnabled = elements.qEnergyLossCheckbox.checked;
        //console.log(`q - Energy Loss enabled: ${isQEnergyLossEnabled}`);
        
        if (isQEnergyLossEnabled !== wasQEnergyLossEnabled) {
            qConversionPerformed = false;
        }
    
        if (!lastUploadedData || !lastUploadedData.explist_shifted_gauss) {
            console.error('No valid data available for Q-Energy Loss processing.');
            updateUploadMessage('No data available for Q-Energy Loss processing.');
            return;
        }
    
        disableButtons();
        showLoadingSpinner();
    
        try {
            if (isQEnergyLossEnabled && !qConversionPerformed) {
                await requestQPlot();
                qConversionPerformed = true;
            } else {
                togglePlotVisibility();
            }
        } catch (error) {
            console.error('Error during Q-Energy Loss processing:', error);
            updateUploadMessage(`Q-Energy Loss processing failed: ${error.message}`);
        } finally {
            hideLoadingSpinner();
            enableButtons();
        }
    }
    
    async function saveSessionData() {
        if (!lastUploadedData || !lastUploadedData.explist_shifted_gauss) {
            console.error('No valid session data to save.');
            return;
        }
    
        try {
            const formData = new FormData();
            console.log('Adding data.json to FormData');
            formData.append('data.json', new Blob([JSON.stringify(lastUploadedData)], { type: 'application/json' }));
    
            formData.append('q_energyloss', isQEnergyLossEnabled ? 'true' : 'false');
    
            console.log('Uploading data to server...');
            const response = await fetch('http://localhost:7654/upload-directory', {
                method: 'POST',
                body: formData,
            });
    
            if (!response.ok) {
                throw new Error(`Server error ${response.status}: ${response.statusText}`);
            }
    
            console.log('Session data saved successfully.');
    
            if (isQEnergyLossEnabled) {
                await requestQPlot();
            }
        } catch (error) {
            console.error('Failed to save session data:', error);
        }
    }  

    async function requestQPlot() {
        if (!lastUploadedData || !lastUploadedData.explist_shifted_gauss) {
            console.error('No explist_shifted_gauss data available for Q-Plot request.');
            updateUploadMessage('No data available to generate Q-Plot.');
            return;
        }
    
        //console.log('Requesting Q-Plot with data:', lastUploadedData);
    
        try {
            const formData = new FormData();
            formData.append('data.json', new Blob([JSON.stringify(lastUploadedData)], { type: 'application/json' }));
            formData.append('q_energyloss', 'true');
    
            const response = await fetch('http://localhost:7654/q-energyloss', {
                method: 'POST',
                body: formData,
            });
    
            if (!response.ok) {
                throw new Error(`Server error ${response.status}: ${response.statusText}`);
            }
    
            const data = await response.json();
            //console.log('Received Q-Plot and updating image.');
    
            if (data.q_plot) {
                updatePreviewImage(data.q_plot, 'url');
            }
    
            if (data.explist_q_converted) {
                lastUploadedData.explist_q_converted = data.explist_q_converted;
                console.log('Stored explist_q_converted path:', lastUploadedData.explist_q_converted);
            } else {
                console.warn('explist_q_converted path was not included in the response.');
            }
    
        } catch (error) {
            console.error('Failed to retrieve Q-Plot:', error);
            throw error;
        }
    }
    
    
    function togglePlotVisibility() {
        //console.log('Toggling plot visibility');
        if (isQEnergyLossEnabled && lastUploadedData.q_plot) {
            updatePreviewImage(lastUploadedData.q_plot, 'bytesio');
        } else if (lastUploadedData.image) {
            updatePreviewImage(lastUploadedData.image, 'url');
        } else {
            console.warn('No image data available to display');
            updateUploadMessage('No image data available for display.');
        }
    }
    

    async function handleFileUpload(event) {
        const files = event ? event.target.files : elements.fileInput.files;
    
        if (files.length === 0) {
            updateUploadMessage('No files selected');
            return;
        }
        
        disableButtons();
        showLoadingSpinner();
    
        const formData = new FormData();
        for (const file of files) {
            formData.append('filePaths', file, file.name);
        }
        
        try {
            updateUploadMessage('Uploading files...');
            const response = await fetch('http://localhost:7654/upload-directory', {
                method: 'POST',
                body: formData,
            });
    
            if (!response.ok) {
                throw new Error(`Server error ${response.status}: ${response.statusText}`);
            }
    
            const data = await response.json();
            lastUploadedData = data;
    
            updateProfilePlots(data.profiles);
            updatePreviewImage(data.image, 'url');
    
            if (isQEnergyLossEnabled) {
                await requestQPlot();
            } else {
                togglePlotVisibility();
            }
            updateUploadMessage('Files uploaded and processed successfully.');
            showModalMessage('Files uploaded and processed successfully.');
        } catch (error) {
            console.error('Failed to upload and process the file:', error);
            updateUploadMessage(`Failed to upload and process the file: ${error.message}`);
        } finally {
            hideLoadingSpinner();
            enableButtons();
        }
    }
    
    function updateProfilePlots(profiles) {
        console.log('Updating profile plots.');
    
        if (!profiles) {
            console.error('Profiles data is undefined or null.');
            return;
        }
    
        if (!profiles.x_profile || !profiles.y_profile) {
            console.error('x_profile or y_profile data is missing.');
            return;
        }
    
        updateProfilePlot(profiles.x_profile, document.getElementById('x_profile_plot'), 'saveImageXProfileBtn');
        updateProfilePlot(profiles.y_profile, document.getElementById('y_profile_plot'), 'saveImageYProfileBtn');
    }
    
    function updateProfilePlot(profileData, plotElement, saveBtnId, dataType = 'url') {
        if (profileData && profileData.image) {
            console.log(`Updating profile plot: ${saveBtnId}`);
    
            let imageUrl;
            
            if (dataType === 'url') {
                const baseUrl = 'http://localhost:7654';
                imageUrl = baseUrl + profileData.image + '?t=' + new Date().getTime();
    
            } else if (dataType === 'base64') {
                imageUrl = 'data:image/png;base64,' + profileData.image;
    
            } else if (dataType === 'bytesio') {
                const blob = new Blob([profileData.image], { type: 'image/png' });
                imageUrl = URL.createObjectURL(blob);
    
            } else {
                console.error('Unsupported data type for image.');
                return;
            }
    
            plotElement.src = imageUrl;
            plotElement.style.display = "block";
            document.getElementById(saveBtnId).style.display = 'inline-block';
    
        } else {
            console.warn(`No profile data available for: ${saveBtnId}`);
        }
    }
    

    function updatePreviewImage(imageData, dataType = 'url') {
        const imgElement = document.getElementById('previewImage');
    
        if (dataType === 'bytesio') {
            if (!imageData.startsWith('data:image/')) {
                imageData = `data:image/png;base64,${imageData}`;
            }
            imgElement.src = imageData;
            imgElement.style.display = 'block';
            console.log('Displaying image from Base64 encoded data.');
        } else {
            let absoluteImageUrl = imageData;
            if (!imageData.startsWith('http://') && !imageData.startsWith('https://')) {
                absoluteImageUrl = `http://localhost:7654${imageData}`;
            }
    
            const timestamp = new Date().getTime();
            const cacheBustedUrl = `${absoluteImageUrl}?t=${timestamp}`;
    
            imgElement.onload = () => {
                imgElement.style.display = 'block';
            };
    
            imgElement.onerror = () => {
                console.error('Error loading image.');
            };
    
            imgElement.src = cacheBustedUrl;
            //console.log(`Updating preview image with URL: ${cacheBustedUrl}`);
        }
    }

    
    function initializeEventListeners() {
        elements.fileInput.addEventListener('change', handleFileUpload);
        elements.viewAllBtn.addEventListener('click', loadImage);
        elements.previewTab.addEventListener('click', loadImage);
        
        elements.saveImageXProfileBtn?.addEventListener('click', () => saveImage(elements.xProfilePlot, 'x_profile.png'));
        elements.exportCSVXProfileBtn?.addEventListener('click', exportCSVFiles);
        elements.saveImageYProfileBtn?.addEventListener('click', () => saveImage(elements.yProfilePlot, 'y_profile.png'));
        elements.exportCSVYProfileBtn?.addEventListener('click', exportCSVFiles);
        
        elements.savePreviewBtn.addEventListener('click', () => {
            if (elements.previewImage) {
                console.log('Save Preview button clicked. Attempting to save the preview image.');
                saveImage(elements.previewImage, 'preview_image.png');
            } else {
                console.error('Preview image not available for saving.');
            }
        });

        elements.exportCSVBtn?.addEventListener('click', exportCSVFiles);

        elements.qEnergyLossCheckbox?.addEventListener('change', handleQEnergyLossChange);
        
        elements.flipUdBtn.addEventListener('click', () => sendTransformRequest('flip_ud'));
        elements.flipLrBtn.addEventListener('click', () => sendTransformRequest('flip_lr'));
        elements.rotateCcw90Btn.addEventListener('click', () => sendTransformRequest('rotate_ccw90'));
        elements.rotateCw90Btn.addEventListener('click', () => sendTransformRequest('rotate_cw90'));
        elements.blurBtn.addEventListener('click', () => sendTransformRequest('blur'));
        elements.sharpenBtn.addEventListener('click', () => sendTransformRequest('sharpen'));
        elements.resetBtn.addEventListener('click', () => sendTransformRequest('reset'));
    }

    async function sendTransformRequest(action) {
        const explistToUse = lastUploadedData.explist_q_converted || lastUploadedData.explist_shifted_gauss;
        
        if (!explistToUse || !action || !lastUploadedData.exptitles) {
            updateUploadMessage('Required data missing for transformation.');
            return;
        }
        
        const dataToSend = {
            action: action,
            explist: explistToUse,
            exptitles: lastUploadedData.exptitles,
        };
        
        const formData = new FormData();
        formData.append('data.json', new Blob([JSON.stringify(dataToSend)], { type: 'application/json' }));
        
        disableButtons();
        showLoadingSpinner();
    
        try {
            const response = await fetch('http://localhost:7654/transform', {
                method: 'POST',
                body: formData,
            });
        
            if (!response.ok) {
                throw new Error(`Server error ${response.status}: ${response.statusText}`);
            }
        
            const result = await response.json();
            if (result.success) {
                updatePreviewImage(result.image, 'bytesio');
                lastUploadedData.explist_q_converted = result.explist_path;
            } else {
                updateUploadMessage(`Transformation failed: ${result.error}`);
            }
        } catch (error) {
            updateUploadMessage(`Error during transformation: ${error.message}`);
        } finally {
            hideLoadingSpinner();
            enableButtons();
        }
    }
    
    async function exportCSVFiles() {
        if (!lastUploadedData || !lastUploadedData.latest_explist || !lastUploadedData.exptitles) {
            updateUploadMessage('No data available to export as CSV');
            return;
        }
    
        disableButtons();
        showLoadingSpinner();
    
        try {
            const response = await fetch('http://localhost:7654/export-csv-files', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    latest_explist: lastUploadedData.latest_explist,  // This is now a file path
                    exptitles: lastUploadedData.exptitles
                })
            });
    
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Server error ${response.status}: ${response.statusText}\n${errorText}`);
            }
    
            const result = await response.json();
            if (result.error) {
                throw new Error(result.error);
            }
    
            // Trigger downloads for each file
            result.files.forEach(filePath => {
                const fileName = filePath.split('/').pop();
                const downloadLink = document.createElement('a');
                downloadLink.href = `http://localhost:7654/download/${encodeURIComponent(fileName)}`;
                downloadLink.download = fileName;
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
            });
    
            updateUploadMessage('CSV files have been generated and download started.');
            showModalMessage('CSV files have been generated and are being downloaded to your default download folder.');
        } catch (error) {
            updateUploadMessage(`Failed to export CSV files: ${error.message}`);
            console.error('Error exporting CSV files:', error);
        } finally {
            hideLoadingSpinner();
            enableButtons();
        }
    }
    
    function saveImage(imageElement, fileName) {
        console.log(`Saving image: ${fileName}`);
    
        if (!imageElement || !imageElement.src) {
            console.error('No image available to save.');
            return;
        }
    
        if (imageElement.src.startsWith('data:image')) {
            const base64Data = imageElement.src.split(',')[1];
            const byteCharacters = atob(base64Data);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], { type: 'image/png' });
    
            const url = URL.createObjectURL(blob);
            downloadImage(url, fileName);
            URL.revokeObjectURL(url);
        } else {
            downloadImage(imageElement.src, fileName);
        }
    }
    
    function downloadImage(url, fileName) {
        const link = document.createElement('a');
        link.href = url;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    function loadImage() {
        if (elements.viewAllBtn.classList.contains('active') && elements.previewTab.classList.contains('active')) {
            if (lastUploadedData) {
                togglePlotVisibility();
            } else {
                console.log('No last uploaded data found, triggering file input change.');
                elements.fileInput.dispatchEvent(new Event('change'));
            }
        }
    }


    function handleReset() {
        if (!initialUploadedData) {
            updateUploadMessage('No data available to reset');
            return;
        }
    
        lastUploadedData = JSON.parse(JSON.stringify(initialUploadedData));
        qConversionPerformed = false; 
        updateProfilePlots(lastUploadedData.profiles);
        togglePlotVisibility();
        updateUploadMessage('Reset to initial state.');
    }
    

    initializeEventListeners();

    return {
        updateUploadMessage,
        getLastUploadedData: () => lastUploadedData,
        getInitialUploadedData: () => initialUploadedData,
        resetToInitialState: handleReset,
        sendTransformRequest,
        exportCSVFiles,
        saveImage
    };
}
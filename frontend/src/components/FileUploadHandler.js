export function initializeFileUploadHandler() {
    const elements = {
        fileInput: document.getElementById('fileInput'),
        previewImage: document.getElementById('previewImage'),
        viewAllBtn: document.getElementById('viewAllBtn'),
        previewTab: document.getElementById('previewTab'),
        xProfileTab: document.querySelector('.tab[data-content="x_profile"]'),
        yProfileTab: document.querySelector('.tab[data-content="y_profile"]'),
        uploadMessage: document.getElementById('uploadMessage'),
        xProfilePlot: document.getElementById('x_profile_plot'),
        yProfilePlot: document.getElementById('y_profile_plot'),
        saveImageXProfileBtn: document.getElementById('saveImageXProfileBtn'), // 수정된 요소 이름
        saveImageYProfileBtn: document.getElementById('saveImageYProfileBtn'), // 수정된 요소 이름
        exportCSVXProfileBtn: document.getElementById('exportCSVXProfileBtn'), // 추가된 요소
        exportCSVYProfileBtn: document.getElementById('exportCSVYProfileBtn'), // 추가된 요소
        blurBtn: document.getElementById('blurBtn'), // 추가된 요소
        sharpenBtn: document.getElementById('sharpenBtn'), // 추가된 요소
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

    console.log('File upload handler initialized.');

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
        console.log(`q - Energy Loss enabled: ${isQEnergyLossEnabled}`);
    
        if (isQEnergyLossEnabled !== wasQEnergyLossEnabled) {
            qConversionPerformed = false;
        }
    
        if (isQEnergyLossEnabled && !qConversionPerformed) {
            try {
                await saveSessionData(); // 세션 데이터 저장
                await requestQPlot(); // Q-Plot 요청
                qConversionPerformed = true;
            } catch (error) {
                console.error('Error during Q-Energy Loss processing:', error);
                updateUploadMessage(`Q-Energy Loss processing failed: ${error.message}`);
            }
        } else {
            togglePlotVisibility(); // 기존 이미지 표시
        }
    }    
    

    async function saveSessionData() {
        try {
            const formData = new FormData();
    
            // 데이터가 올바르게 존재하는지 확인
            if (lastUploadedData && lastUploadedData.explist_shifted_gauss) {
                console.log('Adding data.json to FormData');
                formData.append('data.json', new Blob([JSON.stringify(lastUploadedData)], { type: 'application/json' }));
            } else {
                console.error('lastUploadedData or explist_shifted_gauss is missing');
                return;
            }
    
            // q_energyloss 상태 추가
            console.log('Appending q_energyloss state');
            formData.append('q_energyloss', isQEnergyLossEnabled ? 'true' : 'false');
    
            // FormData에 추가된 항목 확인
            for (let pair of formData.entries()) {
                console.log(`FormData entry - ${pair[0]}: ${pair[1]}`);
            }
    
            console.log('Uploading data to server...');
            const response = await fetch('http://localhost:7654/upload-directory', {
                method: 'POST',
                body: formData,
            });
    
            if (!response.ok) {
                throw new Error(`Server error ${response.status}: ${response.statusText}`);
            }
    
            console.log('Session data saved successfully.');
    
            // 세션 데이터 저장 후 Q-Plot을 요청
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
    
        console.log('Q-Plot을 위한 데이터:', lastUploadedData);
    
        try {
            const formData = new FormData();
            formData.append('data.json', new Blob([JSON.stringify(lastUploadedData)], { type: 'application/json' }));
    
            console.log('보낼 페이로드:', lastUploadedData);
    
            const response = await fetch('http://localhost:7654/q-energyloss', {
                method: 'POST',
                body: formData,
            });
    
            if (!response.ok) {
                throw new Error(`Server error ${response.status}: ${response.statusText}`);
            }
    
            const data = await response.json();
            console.log('Q-Plot 수신 및 이미지 업데이트 중.');
    
            if (data.q_plot) {
                updatePreviewImage(data.q_plot);
            }
    
        } catch (error) {
            console.error('Failed to retrieve Q-Plot:', error);
        }
    }  

    
    function togglePlotVisibility() {
        console.log('Toggling plot visibility');
        if (isQEnergyLossEnabled && lastUploadedData.q_plot) {
            console.log('Displaying Q-Plot');
            updatePreviewImage(lastUploadedData.q_plot);
        } else if (lastUploadedData.image) {
            console.log('Displaying preview image');
            updatePreviewImage(lastUploadedData.image);
        } else {
            console.warn('No image data available to display');
        }
    }

    async function handleFileUpload(event) {
        console.log('handleFileUpload called.');
        const files = event ? event.target.files : elements.fileInput.files;
        if (files.length === 0) {
            console.warn('No files selected.');
            updateUploadMessage('No files selected');
            return;
        }
    
        const formData = new FormData();
    
        for (const file of files) {
            console.log(`Appending file: ${file.name}`);
            formData.append('filePaths', file, file.name);
        }
    
        try {
            updateUploadMessage('Uploading files...');
            console.log('Uploading files to server...');
            const response = await fetch('http://localhost:7654/upload-directory', {
                method: 'POST',
                body: formData,
            });
    
            if (!response.ok) {
                throw new Error(`Server error ${response.status}: ${response.statusText}`);
            }
    
            const data = await response.json();
            console.log('Files uploaded successfully.');
            lastUploadedData = data;
    
            updateProfilePlots(data.profiles);
            updatePreviewImage(data.image);
    
            if (isQEnergyLossEnabled) {
                await requestQPlot();
            } else {
                togglePlotVisibility();
            }
    
            updateUploadMessage('Files uploaded and processed successfully.');
        } catch (error) {
            console.error('Failed to upload and process the file:', error);
            updateUploadMessage(`Failed to upload and process the file: ${error.message}`);
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
    
        updateProfilePlot(profiles.x_profile, elements.xProfilePlot, 'saveImageXProfileBtn');
        updateProfilePlot(profiles.y_profile, elements.yProfilePlot, 'saveImageYProfileBtn');
    }

    
    function updateProfilePlot(profileData, plotElement, saveBtnId) {
        if (profileData && profileData.image) {
            console.log(`Updating profile plot: ${saveBtnId}`);
    
            let imageUrl = profileData.image;
            if (!imageUrl.startsWith('http://') && !imageUrl.startsWith('https://')) {
                imageUrl = `http://localhost:7654${imageUrl}`;
            }
    
            plotElement.src = imageUrl;
            plotElement.style.display = "block";
            document.getElementById(saveBtnId).style.display = 'inline-block';
        } else {
            console.warn(`No profile data available for: ${saveBtnId}`);
        }
    }

    function updatePreviewImage(imageUrl) {
        const imgElement = document.getElementById('previewImage');
    
        let absoluteImageUrl = imageUrl;
        if (!imageUrl.startsWith('http://') && !imageUrl.startsWith('https://')) {
            absoluteImageUrl = `http://localhost:7654${imageUrl}`;
        }
    
        const timestamp = new Date().getTime();
        const cacheBustedUrl = `${absoluteImageUrl}?t=${timestamp}`;
    
        imgElement.onload = () => {
            console.log('Image loaded successfully.');
            imgElement.style.display = 'block';
        };
    
        imgElement.onerror = () => {
            console.error('Error loading image.');
        };
    
        imgElement.src = cacheBustedUrl;
        console.log(`Updating preview image with URL: ${cacheBustedUrl}`);
    }
    
    function initializeEventListeners() {
        console.log('Initializing event listeners.');
        elements.fileInput.addEventListener('change', handleFileUpload);
        elements.viewAllBtn.addEventListener('click', loadImage);
        elements.previewTab.addEventListener('click', loadImage);
        
        if (elements.saveImageXProfileBtn) {  // 수정된 요소 이름
            elements.saveImageXProfileBtn.addEventListener('click', () => saveImage(elements.xProfilePlot, 'x_profile.png'));
        }
        if (elements.exportCSVXProfileBtn) {  // 추가된 이벤트 리스너
            elements.exportCSVXProfileBtn.addEventListener('click', exportCSVFiles);
        }
        if (elements.saveImageYProfileBtn) {  // 수정된 요소 이름
            elements.saveImageYProfileBtn.addEventListener('click', () => saveImage(elements.yProfilePlot, 'y_profile.png'));
        }
        if (elements.exportCSVYProfileBtn) {  // 추가된 이벤트 리스너
            elements.exportCSVYProfileBtn.addEventListener('click', exportCSVFiles);
        }
        if (elements.exportCSVBtn) {
            elements.exportCSVBtn.addEventListener('click', exportCSVFiles);
        }

        if (elements.qEnergyLossCheckbox) {
            elements.qEnergyLossCheckbox.addEventListener('change', handleQEnergyLossChange);
        }

        elements.flipUdBtn.addEventListener('click', () => sendTransformRequest('flip_ud'));
        elements.flipLrBtn.addEventListener('click', () => sendTransformRequest('flip_lr'));
        elements.rotateCcw90Btn.addEventListener('click', () => sendTransformRequest('rotate_ccw90'));
        elements.rotateCw90Btn.addEventListener('click', () => sendTransformRequest('rotate_cw90'));
        elements.blurBtn.addEventListener('click', () => sendTransformRequest('blur')); // 추가된 이벤트 리스너
        elements.sharpenBtn.addEventListener('click', () => sendTransformRequest('sharpen')); // 추가된 이벤트 리스너
        elements.resetBtn.addEventListener('click', () => sendTransformRequest('reset'));
    }

    async function sendTransformRequest(action) {
        console.log(`sendTransformRequest 호출됨, action: ${action}`);
    
        const dataToSend = {
            action: action,
            explist: lastUploadedData.explist_shifted_gauss || [],
            exptitles: lastUploadedData.exptitles || [],
            gauss_peak_y_mean: lastUploadedData.gauss_peak_y_mean || [],
            q_energy_loss_enabled: qConversionPerformed && isQEnergyLossEnabled
        };
    
        if (dataToSend.explist.length === 0) {
            console.error('explist가 비어 있음. 요청 중단됨.');
            return;
        }
    
        console.log("서버로 보낼 데이터:", dataToSend);
    
        try {
            const response = await fetch('http://localhost:7654/transform', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(dataToSend)
            });
    
            if (!response.ok) {
                throw new Error(`서버 오류 ${response.status}: ${response.statusText}`);
            }
    
            const result = await response.json();
            if (result.success) {
                console.log("변환 성공. 결과:", result);
                updatePreviewImage(result.image);
            } else {
                console.error("변환 실패:", result.error);
            }
        } catch (error) {
            console.error("sendTransformRequest에서 오류 발생:", error);
        }
    }
    

    function loadImage() {
        console.log('loadImage called.');
        if (elements.viewAllBtn.classList.contains('active') && elements.previewTab.classList.contains('active')) {
            if (lastUploadedData) {
                console.log('Last uploaded data found, updating preview image.');
                togglePlotVisibility();
            } else {
                console.log('No last uploaded data found, triggering file input change.');
                elements.fileInput.dispatchEvent(new Event('change'));
            }
        }
    }

    function handleReset() {
        if (!initialUploadedData) {
            console.warn('No data available to reset.');
            updateUploadMessage('No data available to reset');
            return;
        }

        lastUploadedData = JSON.parse(JSON.stringify(initialUploadedData));
        qConversionPerformed = false; 
        updateProfilePlots(lastUploadedData.profiles);
        togglePlotVisibility();
        updateUploadMessage('Reset to initial state.');
    }

    async function exportCSVFiles() {
        console.log('exportCSVFiles called.');
        if (!lastUploadedData) {
            updateUploadMessage('No data available to export as CSV');
            return;
        }

        const saveDir = await window.electron.selectSaveDirectory();

        if (!saveDir) {
            updateUploadMessage('No save directory selected');
            return;
        }

        const dataToSend = isQEnergyLossEnabled ? lastUploadedData.explist_q_converted : lastUploadedData.explist_shifted_gauss;
        console.log('Data to send:', dataToSend);

        try {
            const response = await fetch('http://localhost:7654/download-shifted-data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    save_dir: saveDir,
                    explist: dataToSend,
                    exptitles: lastUploadedData.exptitles
                }),
                mode: 'cors',
            });

            if (!response.ok) {
                throw new Error(`Server error ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            const fileUrls = data.file_urls;

            if (fileUrls && fileUrls.length > 0) {
                fileUrls.forEach(fileUrl => downloadImage(fileUrl, ''));
                updateUploadMessage('CSV files exported successfully.');
            } else {
                updateUploadMessage('No CSV files available to export.');
            }
        } catch (error) {
            updateUploadMessage(`Failed to export CSV files: ${error.message}`);
            console.error('Error exporting CSV files:', error);
        }
    }

    function saveImage(imageElement, fileName) {
        console.log(`Saving image: ${fileName}`);
        if (imageElement.src.startsWith('data:image')) {
            downloadImage(imageElement.src, fileName);
        } else {
            fetch(imageElement.src)
                .then(response => response.blob())
                .then(blob => {
                    const url = URL.createObjectURL(blob);
                    downloadImage(url, fileName);
                    URL.revokeObjectURL(url);
                })
                .catch(error => console.error('Error downloading image:', error));
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

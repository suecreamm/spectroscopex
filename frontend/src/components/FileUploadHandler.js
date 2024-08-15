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
        savePreviewBtn: document.getElementById('savePreviewBtn'),
        saveXProfileBtn: document.getElementById('saveXProfileBtn'),
        saveYProfileBtn: document.getElementById('saveYProfileBtn'),
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
    let qConversionPerformed = false; // q_conversion이 이미 수행되었는지 여부를 추적

    let lastValidExplist = [];
    let lastValidExptitles = [];

    function saveLastValidData(dataToSend) {
        if (dataToSend.explist && dataToSend.explist.length > 0) {
            lastValidExplist = dataToSend.explist;
        }
        if (dataToSend.exptitles && dataToSend.exptitles.length > 0) {
            lastValidExptitles = dataToSend.exptitles;
        }
    }

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
            qConversionPerformed = false;  // 체크박스 상태가 바뀌었으므로 qConversion을 다시 수행해야 함
        }

        if (isQEnergyLossEnabled && !qConversionPerformed) {
            await requestQPlot(); // q_conversion 수행 후 플롯 갱신
            qConversionPerformed = true;
        } else {
            togglePlotVisibility(); // Q-Energy Loss 토글을 켰을 때, 변환된 데이터 표시
        }
    }

    async function sendTransformRequest(action) {
        console.log(`sendTransformRequest called with action: ${action}`);

        const dataToSend = {
            action: action,
            explist: lastUploadedData.explist_shifted_gauss || [],
            exptitles: lastUploadedData.exptitles || [],
            gauss_peak_y_mean: lastUploadedData.gauss_peak_y_mean || [],
            q_energy_loss_enabled: qConversionPerformed && isQEnergyLossEnabled // q_conversion이 수행된 경우만 true
        };

        if (dataToSend.explist.length === 0) {
            console.error('explist is empty. Aborting request.');
            return;
        }

        console.log("Data to send:", dataToSend);

        try {
            console.log("Sending transform request to server...");
            const response = await fetch('http://localhost:7654/transform', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(dataToSend)
            });

            if (!response.ok) {
                throw new Error(`Server error ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            if (result.success) {
                console.log("Transformation successful. Result:", result);
                updatePreviewImage(result.image);
                saveLastValidData(result); // 변환 후 마지막 데이터 저장
            } else {
                console.error("Transformation failed:", result.error);
            }
        } catch (error) {
            console.error("Error in sendTransformRequest:", error);
        }
    }

    initializeEventListeners();

    function initializeEventListeners() {
        console.log('Initializing event listeners.');
        elements.fileInput.addEventListener('change', handleFileUpload);
        elements.viewAllBtn.addEventListener('click', loadImage);
        elements.previewTab.addEventListener('click', loadImage);
        elements.xProfileTab.addEventListener('click', () => loadProfile('x'));
        elements.yProfileTab.addEventListener('click', () => loadProfile('y'));

        if (elements.savePreviewBtn) {
            elements.savePreviewBtn.addEventListener('click', () => saveImage(elements.previewImage, 'preview.png'));
        }
        if (elements.saveXProfileBtn) {
            elements.saveXProfileBtn.addEventListener('click', () => saveImage(elements.xProfilePlot, 'x_profile.png'));
        }
        if (elements.saveYProfileBtn) {
            elements.saveYProfileBtn.addEventListener('click', () => saveImage(elements.yProfilePlot, 'y_profile.png'));
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
        elements.resetBtn.addEventListener('click', () => sendTransformRequest('reset'));
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

        if (isQEnergyLossEnabled) {
            console.log('Appending q_energyloss to form data.');
            formData.append('q_energyloss', 'true');
        }

        try {
            updateUploadMessage('Uploading files...');
            console.log('Uploading files to server...');
            const response = await fetch('http://localhost:7654/upload-directory', {
                method: 'POST',
                body: formData,
                mode: 'cors',
            });

            if (!response.ok) {
                throw new Error(`Server error ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('Files uploaded successfully.');
            lastUploadedData = data;
            if (!initialUploadedData) {
                initialUploadedData = JSON.parse(JSON.stringify(data));
                console.log('Initial uploaded data stored.');
            }

            updateProfilePlots(data.profiles);

            updatePreviewImage(data.image);

            // 파일 업로드 후 자동으로 Q-Energy Loss 플롯 요청
            if (isQEnergyLossEnabled) {
                await requestQPlot();
                qConversionPerformed = true; // q_conversion이 완료되었음을 기록
            }

            updateUploadMessage('Files uploaded and processed successfully.');
        } catch (error) {
            console.error('Failed to upload and process the file:', error);
            updateUploadMessage(`Failed to upload and process the file: ${error.message}`);
        }
    }

    async function requestQPlot() {
        if (!lastUploadedData || !lastUploadedData.explist_shifted_gauss) {
            console.error('No explist_shifted_gauss data available for Q-Plot request.');
            updateUploadMessage('No data available to generate Q-Plot.');
            return;
        }

        try {
            const payload = {
                action: 'q_conversion',
                explist: lastUploadedData.explist_shifted_gauss,
                exptitles: lastUploadedData.exptitles,
                gauss_peak_y_mean: lastUploadedData.gauss_peak_y_mean,
                q_energy_loss_enabled: true,
            };

            const response = await fetch('http://localhost:7654/transform', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error(`Server error ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('Q-Plot received and updating image.');

            if (data.image) {
                updatePreviewImage(data.image);
                lastUploadedData.explist = data.explist_q_converted || lastUploadedData.explist; // 업데이트된 리스트 저장
            }

        } catch (error) {
            console.error('Failed to retrieve Q-Plot:', error);
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

    function loadProfile(axis) {
        console.log(`Loading ${axis}-profile`);
        const isXProfile = axis === 'x';
        const profilePlot = isXProfile ? elements.xProfilePlot : elements.yProfilePlot;

        if (lastUploadedData && lastUploadedData.profiles) {
            const profileData = isXProfile ? lastUploadedData.profiles.x_profile : lastUploadedData.profiles.y_profile;
            if (profileData && profileData.image) {
                profilePlot.src = profileData.image;
                profilePlot.style.display = "block";
            } else {
                console.error(`No ${axis.toUpperCase()}-profile image data available`);
            }
        } else {
            console.log(`No uploaded data available for ${axis.toUpperCase()}-profile, triggering file input`);
            elements.fileInput.dispatchEvent(new Event('change'));
        }
    }

    function updateProfilePlots(profiles) {
        console.log('Updating profile plots.');
        updateProfilePlot(profiles.x_profile, elements.xProfilePlot, 'saveXProfileBtn');
        updateProfilePlot(profiles.y_profile, elements.yProfilePlot, 'saveYProfileBtn');
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

    function handleReset() {
        if (!initialUploadedData) {
            console.warn('No data available to reset.');
            updateUploadMessage('No data available to reset');
            return;
        }

        lastUploadedData = JSON.parse(JSON.stringify(initialUploadedData));
        qConversionPerformed = false; // 초기화 시 qConversion 상태도 초기화
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

// FileUploadHandler.js

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
    let updateTransformImage = null;
    let isQEnergyLossEnabled = false;

    if (Object.values(elements).some(element => !element)) {
        console.error('One or more required elements not found');
        return;
    }

    initializeEventListeners();

    function initializeEventListeners() {
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

        // q-Energy Loss 체크박스 변경 시 상태 업데이트
        if (elements.qEnergyLossCheckbox) {
            elements.qEnergyLossCheckbox.addEventListener('change', handleQEnergyLossChange);
        }

        // Transform 버튼 이벤트 리스너
        elements.flipUdBtn.addEventListener('click', () => sendTransformRequest('flip_ud'));
        elements.flipLrBtn.addEventListener('click', () => sendTransformRequest('flip_lr'));
        elements.rotateCcw90Btn.addEventListener('click', () => sendTransformRequest('rotate_ccw90'));
        elements.rotateCw90Btn.addEventListener('click', () => sendTransformRequest('rotate_cw90'));
        elements.resetBtn.addEventListener('click', handleReset);
    }

    function handleQEnergyLossChange() {
        isQEnergyLossEnabled = elements.qEnergyLossCheckbox.checked;
        console.log(`q - Energy Loss enabled: ${isQEnergyLossEnabled}`);
        if (isQEnergyLossEnabled) {
            handleFileUpload(); // 파일 업로드를 다시 실행하여 데이터 업데이트
        }
    }

    async function handleFileUpload(event) {
        const files = event ? event.target.files : elements.fileInput.files;
        if (files.length === 0) {
            updateUploadMessage('No files selected');
            return;
        }

        const formData = new FormData();
        let defaultSaveDir = '';

        for (const file of files) {
            formData.append('filePaths', file, file.name);
            const filePath = file.webkitRelativePath || file.name; 
            if (!defaultSaveDir && filePath.includes('/')) {
                defaultSaveDir = filePath.substring(0, filePath.lastIndexOf('/'));
            }
        }

        // q-Energyloss 체크 여부를 formData에 추가
        if (isQEnergyLossEnabled) {
            formData.append('q_energyloss', 'true');
        }

        try {
            updateUploadMessage('Uploading files...');
            const response = await fetch('http://localhost:7654/upload-directory', {
                method: 'POST',
                body: formData,
                mode: 'cors',
            });

            if (!response.ok) {
                throw new Error(`Server error ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            lastUploadedData = data;
            if (!initialUploadedData) {
                initialUploadedData = JSON.parse(JSON.stringify(data));
            }
            lastUploadedData.defaultSaveDir = defaultSaveDir;
            updatePreviewImage(data.image);
            updateProfilePlots(data.profiles);

            // q 변환 플롯이 반환된 경우, 이를 UI에 표시
            if (data.q_plot) {
                updatePreviewImage(data.q_plot, 'qPlotImage');
            }

            if (updateTransformImage) {
                updateTransformImage(data.image);
            }
            activatePreviewTab();
            updateUploadMessage('Files uploaded and processed successfully.');
        } catch (error) {
            updateUploadMessage(`Failed to upload and process the file: ${error.message}`);
            console.error('Error:', error);
        }
    }

    function updatePreviewImage(imageUrl, targetId = 'previewImage') {
        const imgElement = document.getElementById(targetId);
        imgElement.src = imageUrl;
        imgElement.style.display = 'block';
    }

    function updateProfilePlots(profiles) {
        updateProfilePlot(profiles.x_profile, elements.xProfilePlot, 'saveXProfileBtn');
        updateProfilePlot(profiles.y_profile, elements.yProfilePlot, 'saveYProfileBtn');
    }

    function updateProfilePlot(profileData, plotElement, saveBtnId) {
        if (profileData && profileData.image) {
            plotElement.src = profileData.image;
            plotElement.style.display = "block";
            document.getElementById(saveBtnId).style.display = 'inline-block';
        }
    }

    function activatePreviewTab() {
        activateTab(elements.previewTab);
    }

    function activateTab(tab) {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tabPanel').forEach(tabPanel => {
            tabPanel.classList.remove('active');
            tabPanel.style.display = 'none';
        });

        tab.classList.add('active');
        const contentId = tab.getAttribute('data-content');
        const tabPanel = document.getElementById(contentId);
        if (tabPanel) {
            tabPanel.classList.add('active');
            tabPanel.style.display = 'block';
        }
        elements.viewAllBtn.classList.add('active');
    }

    function loadImage() {
        if (elements.viewAllBtn.classList.contains('active') && elements.previewTab.classList.contains('active')) {
            if (lastUploadedData) {
                updatePreviewImage(lastUploadedData.image);
            } else {
                elements.fileInput.dispatchEvent(new Event('change'));
            }
        }
    }

    function loadProfile(axis) {
        const isXProfile = axis === 'x';
        const profileTab = isXProfile ? elements.xProfileTab : elements.yProfileTab;
        const profilePlot = isXProfile ? elements.xProfilePlot : elements.yProfilePlot;
    
        if (elements.viewAllBtn.classList.contains('active') && profileTab.classList.contains('active')) {
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
    }
    

    function saveImage(imageElement, fileName) {
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

    async function exportCSVFiles() {
        if (!lastUploadedData) {
            updateUploadMessage('No data available to export as CSV');
            return;
        }
    
        const saveDir = await window.electron.selectSaveDirectory();
    
        if (!saveDir) {
            updateUploadMessage('No save directory selected');
            return;
        }
    
        try {
            const response = await fetch('http://localhost:7654/download-shifted-data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    save_dir: saveDir,
                    filePaths: lastUploadedData.filePaths
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

    async function transformImage(action, qEnergyLossEnabled) {
        try {
            console.log('Transforming image:', action);
            const response = await fetch('http://localhost:7654/transform', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    action: action,
                    q_energy_loss_enabled: qEnergyLossEnabled
                }),
                mode: 'cors',
            });
    
            if (!response.ok) {
                throw new Error(`Server error ${response.status}: ${response.statusText}`);
            }
    
            const data = await response.json();
            if (data.success) {
                return { success: true, image: data.image };
            } else {
                throw new Error(data.error || 'Unknown error occurred');
            }
        } catch (error) {
            console.error('Error in transformImage:', error);
            throw error;
        }
    }

    function sendTransformRequest(action) {
        const qEnergyLossEnabled = isQEnergyLossEnabled;
        fileUploadHandler.updateUploadMessage('Transforming image...');
        return transformImage(action, qEnergyLossEnabled)
            .then(response => {
                if (response.success) {
                    updateTransformImage(response.image);
                    updateUploadMessage('Image transformed successfully.');
                }
            })
            .catch(error => {
                updateUploadMessage(`Transform failed: ${error.message}`);
            });
    }

    function handleReset() {
        const qEnergyLossEnabled = isQEnergyLossEnabled;
        sendTransformRequest('reset', qEnergyLossEnabled);
    }

    function updateUploadMessage(message) {
        if (elements.uploadMessage) {
            elements.uploadMessage.textContent = message;
        } else {
            console.error('Upload message element not found');
        }
    }

    return {
        updateUploadMessage,
        getLastUploadedData: () => lastUploadedData,
        getInitialUploadedData: () => initialUploadedData,
        setUpdateTransformImage: (func) => {
            updateTransformImage = func;
        },
        resetToInitialState: () => {
            if (initialUploadedData) {
                updatePreviewImage(initialUploadedData.image);
                updateProfilePlots(initialUploadedData.profiles);
                if (updateTransformImage) {
                    updateTransformImage(initialUploadedData.image);
                }
                lastUploadedData = JSON.parse(JSON.stringify(initialUploadedData));
                updateUploadMessage('Reset to initial state.');
            } else {
                updateUploadMessage('No initial state available.');
            }
        },
        saveImage,
        exportCSVFiles,
        transformImage,
        isQEnergyLossEnabled: () => isQEnergyLossEnabled 
    };
}

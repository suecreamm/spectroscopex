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
        exportCSVBtn: document.getElementById('exportCSVBtn')
    };

    let lastUploadedData = null;
    let initialUploadedData = null;
    let updateTransformImage = null;

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
    }

    async function handleFileUpload(event) {
        const files = event.target.files;
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

    function updatePreviewImage(imageUrl) {
        elements.previewImage.src = imageUrl;
        elements.previewImage.alt = "Plot Image";
        elements.previewImage.style.display = "block";
        elements.previewImage.style.margin = "0 auto";
    }

    function updateProfilePlots(profiles) {
        updateProfilePlot(profiles.x_profile, elements.xProfilePlot, 'saveXProfileBtn');
        updateProfilePlot(profiles.y_profile, elements.yProfilePlot, 'saveYProfileBtn');
    }

    function updateProfilePlot(profileData, plotElement, saveBtnId) {
        if (profileData && profileData.image) {
            plotElement.src = `data:image/png;base64,${profileData.image}`;
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
                    profilePlot.src = `data:image/png;base64,${profileData.image}`;
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

    async function transformImage(action) {
        try {
            console.log('Transforming image:', action);
            const response = await window.electron.transformImage(action);
            console.log('Transform response:', response);
            if (response.success && response.image) {
                if (updateTransformImage) {
                    updateTransformImage(response.image);
                }
                return { success: true, image: response.image };
            } else {
                throw new Error(response.error || 'Unknown error occurred');
            }
        } catch (error) {
            console.error('Error in transformImage:', error);
            throw error;
        }
    }

    function updateUploadMessage(message) {
        elements.uploadMessage.textContent = message;
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
        transformImage
    };
}
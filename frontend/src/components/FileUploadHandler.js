export function initializeFileUploadHandler() {
    const fileInput = document.getElementById('fileInput');
    const previewImage = document.getElementById('previewImage');
    const viewAllBtn = document.getElementById('viewAllBtn');
    const previewTab = document.querySelector('.tab[data-content="preview"]');
    const xProfileTab = document.querySelector('.tab[data-content="x_profile"]');
    const yProfileTab = document.querySelector('.tab[data-content="y_profile"]');
    const uploadMessage = document.getElementById('uploadMessage');
    const xProfilePlot = document.getElementById('x_profile_plot');
    const yProfilePlot = document.getElementById('y_profile_plot');
    const savePreviewBtn = document.getElementById('savePreviewBtn');
    const saveXProfileBtn = document.getElementById('saveXProfileBtn');
    const saveYProfileBtn = document.getElementById('saveYProfileBtn');
    const saveCSVBtn = document.getElementById('saveCSVBtn'); // CSV 저장 버튼

    if (!fileInput || !previewImage || !viewAllBtn || !previewTab || !xProfileTab || !yProfileTab || !uploadMessage || !xProfilePlot || !yProfilePlot) {
        console.error('One or more required elements not found');
        return;
    }

    if (savePreviewBtn) {
        savePreviewBtn.addEventListener('click', () => saveImage(previewImage, 'preview.png'));
    }
    if (saveXProfileBtn) {
        saveXProfileBtn.addEventListener('click', () => saveImage(xProfilePlot, 'x_profile.png'));
    }
    if (saveYProfileBtn) {
        saveYProfileBtn.addEventListener('click', () => saveImage(yProfilePlot, 'y_profile.png'));
    }
    if (saveCSVBtn) {
        saveCSVBtn.addEventListener('click', saveCSVFiles); // CSV 파일 저장 버튼 클릭 이벤트 핸들러
    }

    fileInput.addEventListener('change', handleFileUpload);
    viewAllBtn.addEventListener('click', loadImage);
    previewTab.addEventListener('click', loadImage);
    xProfileTab.addEventListener('click', () => loadProfile('x'));
    yProfileTab.addEventListener('click', () => loadProfile('y'));

    let lastUploadedData = null;

    async function handleFileUpload(event) {
        const files = event.target.files;
        if (files.length === 0) {
            console.error('No files selected');
            uploadMessage.textContent = 'No files selected';
            return;
        }

        const formData = new FormData();
        let defaultSaveDir = '';

        for (const file of files) {
            formData.append('filePaths', file, file.name);

            // 파일 경로에서 디렉토리 경로 추출
            const filePath = file.webkitRelativePath || file.name; 
            if (!defaultSaveDir && filePath.includes('/')) {
                defaultSaveDir = filePath.substring(0, filePath.lastIndexOf('/'));
            }
        }

        try {
            uploadMessage.textContent = 'Uploading files...';
            const response = await fetch('http://localhost:7654/upload-directory', {
                method: 'POST',
                body: formData,
                mode: 'cors',
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Server error ${response.status}: ${response.statusText}. ${errorText}`);
            }

            const data = await response.json();
            lastUploadedData = data;
            lastUploadedData.defaultSaveDir = defaultSaveDir; // defaultSaveDir을 lastUploadedData에 저장
            updatePreviewImage(data.image);
            updateProfilePlots(data.profiles);
            activatePreviewTab();
            uploadMessage.textContent = 'Files uploaded and processed successfully.';
        } catch (error) {
            uploadMessage.textContent = `Failed to upload and process the file: ${error.message}`;
            console.error('Error:', error);
        }
    }

    function updatePreviewImage(imageUrl) {
        previewImage.src = imageUrl;
        previewImage.alt = "Plot Image";
        previewImage.style.display = "block";
        previewImage.style.margin = "0 auto";
    }

    function updateProfilePlots(profiles) {
        if (profiles.x_profile && profiles.x_profile.image) {
            xProfilePlot.src = `data:image/png;base64,${profiles.x_profile.image}`;
            xProfilePlot.style.display = "block";
            document.getElementById('saveXProfileBtn').style.display = 'inline-block';
        }
        if (profiles.y_profile && profiles.y_profile.image) {
            yProfilePlot.src = `data:image/png;base64,${profiles.y_profile.image}`;
            yProfilePlot.style.display = "block";
            document.getElementById('saveYProfileBtn').style.display = 'inline-block';
        }
    }

    function activatePreviewTab() {
        activateTab(previewTab);
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
        viewAllBtn.classList.add('active');
    }

    function loadImage() {
        if (viewAllBtn.classList.contains('active') && previewTab.classList.contains('active')) {
            if (lastUploadedData) {
                updatePreviewImage(lastUploadedData.image);
            } else {
                const changeEvent = new Event('change');
                fileInput.dispatchEvent(changeEvent);
            }
        }
    }

    function loadProfile(axis) {
        const isXProfile = axis === 'x';
        const profileTab = isXProfile ? xProfileTab : yProfileTab;
        const profilePlot = isXProfile ? xProfilePlot : yProfilePlot;

        if (viewAllBtn.classList.contains('active') && profileTab.classList.contains('active')) {
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
                const changeEvent = new Event('change');
                fileInput.dispatchEvent(changeEvent);
            }
        }
    }

    // Save the image currently displayed in the specified element
    function saveImage(imageElement, fileName) {
        if (imageElement.src.startsWith('data:image')) {
            const link = document.createElement('a');
            link.href = imageElement.src;
            link.download = fileName;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } else {
            fetch(imageElement.src)
                .then(response => response.blob())
                .then(blob => {
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = fileName;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    URL.revokeObjectURL(url);
                })
                .catch(error => console.error('Error downloading image:', error));
        }
    }

    async function saveCSVFiles() {
        if (!lastUploadedData) {
            console.error('No data available to save as CSV');
            uploadMessage.textContent = 'No data available to save as CSV';
            return;
        }
    
        // 폴더 선택 대화창을 한 번만 띄움
        const saveDir = await window.electron.selectSaveDirectory();
    
        if (!saveDir) {
            console.error('No save directory selected');
            uploadMessage.textContent = 'No save directory selected';
            return;
        }
    
        try {
            const response = await fetch('http://localhost:7654/download-shifted-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    save_dir: saveDir, // 선택한 폴더를 서버로 전송
                    filePaths: lastUploadedData.filePaths
                }),
                mode: 'cors',
            });
    
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Server error ${response.status}: ${response.statusText}. ${errorText}`);
            }
    
            const data = await response.json();
            const fileUrls = data.file_urls;
    
            if (fileUrls && fileUrls.length > 0) {
                fileUrls.forEach((fileUrl) => {
                    const link = document.createElement('a');
                    link.href = fileUrl;
                    link.download = ''; // 서버에서 제공하는 파일명을 사용하여 자동으로 다운로드
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                });
                uploadMessage.textContent = 'CSV files downloaded successfully.';
            } else {
                uploadMessage.textContent = 'No CSV files available to download.';
            }
        } catch (error) {
            uploadMessage.textContent = `Failed to download CSV files: ${error.message}`;
            console.error('Error downloading CSV files:', error);
        }
    }
    
}

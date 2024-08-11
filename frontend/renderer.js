let isProcessing = false;

function addSelectDirectoryListener() {
    const selectDirectoryBtn = document.getElementById('selectDirectoryBtn');
    selectDirectoryBtn.removeEventListener('click', handleSelectDirectory);
    selectDirectoryBtn.addEventListener('click', handleSelectDirectory);
    console.log('Select directory listener added');
}

async function handleSelectDirectory() {
    console.log('handleSelectDirectory called'); // 디버그 로그 추가

    if (isProcessing) {
        console.log('A directory selection is already in progress');
        return;
    }

    try {
        isProcessing = true;
        const selectDirectoryBtn = document.getElementById('selectDirectoryBtn');
        selectDirectoryBtn.disabled = true;

        console.log('Calling window.electron.selectDirectory()'); // 디버그 로그 추가
        const directoryPath = await window.electron.selectDirectory();
        console.log('Selected directory path:', directoryPath); // 디버그 로그 추가

        if (directoryPath) {
            await sendDirectoryPathToServer(directoryPath);
        } else {
            console.log('No directory selected'); // 디버그 로그 추가
        }
    } catch (error) {
        console.error('Failed to select directory:', error);
        showError('Failed to select directory. Please try again.');
    } finally {
        isProcessing = false;
        const selectDirectoryBtn = document.getElementById('selectDirectoryBtn');
        selectDirectoryBtn.disabled = false;
    }
}

async function sendDirectoryPathToServer(directoryPath) {
    try {
        console.log('Sending directory path to server:', directoryPath); // 디버그 로그 추가
        const result = await window.electron.uploadDirectory(directoryPath);
        console.log('Server response:', result);
        // 여기에서 결과를 처리하거나 UI를 업데이트할 수 있습니다.
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to upload directory. Please try again.');
    }
}

function showError(message) {
    const errorElement = document.getElementById('errorMessage');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    } else {
        alert(message);
    }
}

// 페이지 로드 시 리스너 추가
document.addEventListener('DOMContentLoaded', addSelectDirectoryListener);
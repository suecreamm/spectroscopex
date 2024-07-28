// "Select Directory" 버튼 클릭 시 디렉토리 선택
document.getElementById('selectDirectoryBtn').addEventListener('click', async () => {
    try {
      // 메인 프로세스에서 디렉토리 경로 가져오기
      const directoryPath = await window.electron.selectDirectory();
      if (directoryPath) {
          sendDirectoryPathToServer(directoryPath);
      }
    } catch (error) {
      console.error('Failed to select directory:', error);
    }
  });
  
  function sendDirectoryPathToServer(directoryPath) {
    fetch('http://localhost:5000/upload-directory', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ directoryPath })
    })
    .then(response => response.json())
    .then(result => {
        console.log('Server response:', result);
        // 여기에서 결과를 처리하거나 UI를 업데이트할 수 있습니다.
    })
    .catch(error => console.error('Error:', error));
  }
  
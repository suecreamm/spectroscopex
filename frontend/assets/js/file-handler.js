// 파일 입력 변경 이벤트 핸들러
document.getElementById('fileInput').addEventListener('change', async function(event) {
  const files = event.target.files;
  if (files.length === 0) {
      console.error('No files selected');
      return;
  }

  const formData = new FormData();
  for (const file of files) {
      formData.append('filePaths', file, file.name);
  }

  try {
      const response = await fetch('http://localhost:7654/upload-directory', {
          method: 'POST',
          body: formData,
      });

      if (!response.ok) {
          throw new Error(`Server error ${response.status}: ${response.statusText}`);
      }

      const blob = await response.blob();
      const imageUrl = URL.createObjectURL(blob);

      const previewElement = document.getElementById('previewImage');
      previewElement.src = imageUrl;
      previewElement.style.display = 'block'; // 이미지가 보이도록 설정

      // 모든 탭과 콘텐츠 비활성화
      document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
      document.querySelectorAll('.content').forEach(content => {
          content.classList.remove('active');
          content.style.display = 'none'; // 모든 콘텐츠를 숨김
      });

      // Preview 및 View All 탭 활성화
      const previewTab = document.querySelector('.tab[data-content="preview"]');
      const previewContent = document.getElementById('preview');
      const viewAllBtn = document.getElementById('viewAllBtn');

      previewTab.classList.add('active');
      previewContent.classList.add('active');
      previewContent.style.display = 'block'; // 'preview' 콘텐츠를 보이도록 설정
      viewAllBtn.classList.add('active');

  } catch (error) {
      console.error('Error sending file paths:', error);
  }
});

// 탭 클릭 이벤트 핸들러 추가
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', function() {
      // 모든 탭과 콘텐츠 비활성화
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.content').forEach(content => {
          content.classList.remove('active');
          content.style.display = 'none';
      });

      // 클릭된 탭 및 해당 콘텐츠 활성화
      tab.classList.add('active');
      const contentId = tab.getAttribute('data-content');
      const content = document.getElementById(contentId);
      content.classList.add('active');
      content.style.display = 'block'; // 콘텐츠를 보이도록 설정
  });
});

document.addEventListener('DOMContentLoaded', function () {
  const fileInput = document.getElementById('fileInput');
  const previewImage = document.getElementById('previewImage'); // 이미지가 표시될 요소
  const viewAllBtn = document.getElementById('viewAllBtn');
  const previewTab = document.querySelector('.tab[data-content="preview"]');
  const uploadMessage = document.getElementById('uploadMessage');

  fileInput.addEventListener('change', async function (event) {
      const files = event.target.files;
      if (files.length === 0) {
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
              throw new Error('Network response was not ok');
          }

          const blob = await response.blob();
          const imgUrl = URL.createObjectURL(blob);
          previewImage.innerHTML = '';
          previewImage.src = imgUrl;
          previewImage.alt = "Plot Image";
          previewImage.style.display = "block";
          previewImage.style.margin = "0 auto";
      } catch (error) {
          uploadMessage.textContent = 'Failed to upload and process the file.';
          console.error('Error:', error);
      }
  });

  function loadImage() {
      if (viewAllBtn.classList.contains('active') && previewTab.classList.contains('active')) {
          const changeEvent = new Event('change');
          fileInput.dispatchEvent(changeEvent);
      }
  }

  viewAllBtn.addEventListener('click', loadImage);
  previewTab.addEventListener('click', loadImage);
});

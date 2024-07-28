document.addEventListener('DOMContentLoaded', function () {
    const fileInput = document.getElementById('fileInput');
    const heatmapCanvas = document.getElementById('heatmapCanvas');
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
        heatmapCanvas.innerHTML = '';  // Clear previous image
        const img = document.createElement('img');
        img.src = imgUrl;
        img.alt = "Plot Image";
        img.style.maxWidth = "100%";
        img.style.display = "block";
        img.style.margin = "0 auto";
        heatmapCanvas.appendChild(img);
      } catch (error) {
        uploadMessage.textContent = 'Failed to upload and process the file.';
        console.error('Error:', error);
      }
    });
  
    function loadHeatmap() {
      // Function to load heatmap if "View All" and "Preview" are active
      if (viewAllBtn.classList.contains('active') && previewTab.classList.contains('active')) {
        const changeEvent = new Event('change');
        fileInput.dispatchEvent(changeEvent);
      }
    }
  
    // Add event listeners to check if "View All" and "Preview" tabs are active
    viewAllBtn.addEventListener('click', loadHeatmap);
    previewTab.addEventListener('click', loadHeatmap);
  });
  
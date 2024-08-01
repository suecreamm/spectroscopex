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
  
    if (!fileInput || !previewImage || !viewAllBtn || !previewTab || !xProfileTab || !yProfileTab || !uploadMessage || !xProfilePlot || !yProfilePlot) {
        console.error('One or more required elements not found');
        return;
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
                mode: 'cors',
            });
  
            if (!response.ok) {
                throw new Error(`Server error ${response.status}: ${response.statusText}`);
            }
  
            const data = await response.json();
            lastUploadedData = data;  // 데이터 저장
            updatePreviewImage(data.image);
            updateProfilePlots(data.profiles);
            activatePreviewTab();
        } catch (error) {
            uploadMessage.textContent = 'Failed to upload and process the file.';
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
        if (profiles.x_profile) {
            xProfilePlot.src = profiles.x_profile.image;
            xProfilePlot.style.display = "block";
        }
        if (profiles.y_profile) {
            yProfilePlot.src = profiles.y_profile.image;
            yProfilePlot.style.display = "block";
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
  
  function updateProfilePlots(profiles) {
      if (profiles.x_profile && profiles.x_profile.image) {
          xProfilePlot.src = `data:image/png;base64,${profiles.x_profile.image}`;
          xProfilePlot.style.display = "block";
      }
      if (profiles.y_profile && profiles.y_profile.image) {
          yProfilePlot.src = `data:image/png;base64,${profiles.y_profile.image}`;
          yProfilePlot.style.display = "block";
      }
  }
  
  }
  
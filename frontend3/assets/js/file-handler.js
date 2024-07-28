let currentFileIndex = 0;
let parsedData = [];

// Handle CSV file upload
document.getElementById('fileInput').addEventListener('change', function(event) {
    const files = event.target.files;
    if (files.length > 0) {
        document.getElementById('uploadMessage').style.display = 'none';
        document.getElementById('heatmapCanvas').style.height = '500px';
        document.querySelector('.tab-action-buttons').style.display = 'flex';
        currentFileIndex = 0;
        parsedData = [];

        Array.from(files).forEach((file, index) => {
            const reader = new FileReader();
            reader.onload = function(e) {
                const csv = e.target.result;
                Papa.parse(csv, {
                    header: false,
                    dynamicTyping: true,
                    complete: function(results) {
                        parsedData.push({ data: results.data, name: file.name });
                        if (index === 0) {
                            updateView();
                        }
                    }
                });
            };
            reader.readAsText(file);
        });

        // Initialize view after files are loaded
        initializeViewAfterUpload();
    } else {
        document.getElementById('uploadMessage').style.display = 'block';
        document.getElementById('heatmapCanvas').style.height = '0';
        document.querySelector('.tab-action-buttons').style.display = 'none';
    }
});

// Update view mode (All or One) based on selected tab and button
function updateView() {
    const activeTab = document.querySelector('.tabs .tab.active').dataset.content;
    const viewMode = document.querySelector('.tab-action-button.active').id;

    if (activeTab === 'preview') {
        if (viewMode === 'viewAllBtn') {
            createHeatmap(parsedData);
        } else if (viewMode === 'viewOneBtn') {
            showSingleFile(currentFileIndex);
        }
    }
}

// Create heatmap for all data
function createHeatmap(data) {
    const heatmapData = data.map((file, index) => ({
        z: file.data,
        x: file.data.map((_, idx) => idx),
        y: file.data[0].map((_, idx) => idx),
        type: 'heatmap',
        colorscale: 'Inferno',
        name: file.name
    }));

    const layout = {
        title: 'CSV Data Heatmap',
        xaxis: { title: 'Index' },
        yaxis: { title: 'Columns' }
    };

    Plotly.newPlot('heatmapCanvas', heatmapData, layout);
}

// Show single file heatmap
function showSingleFile(index) {
    const file = parsedData[index];
    if (!file) return;

    const xValues = file.data.map((_, idx) => idx);
    const yValues = file.data[0].map((_, idx) => idx);
    const zValues = file.data;

    const heatmapData = [{
        z: zValues,
        x: xValues,
        y: yValues,
        type: 'heatmap',
        colorscale: 'Inferno'
    }];

    const layout = {
        title: `CSV Data Heatmap - File: ${file.name}`,
        xaxis: { title: 'Index' },
        yaxis: { title: 'Columns' }
    };

    Plotly.newPlot('heatmapCanvas', heatmapData, layout);

    // Update navigation button visibility
    updateButtonVisibility();
}

// Check if there are any uploaded files with data
function hasFileData() {
    return parsedData.length > 0;
}

// Update content visibility based on file data availability
function updateContentVisibility() {
    const contents = document.querySelectorAll('.content');
    contents.forEach(content => {
        if (hasFileData()) {
            content.style.display = 'block';
        } else {
            content.style.display = 'none';
        }
    });

    // Ensure the action buttons are visible
    document.querySelectorAll('.tab-action-buttons').forEach(buttonGroup => {
        buttonGroup.style.display = 'flex';
    });
}

// Initialization after files are uploaded
function initializeViewAfterUpload() {
    updateView();
    updateButtonVisibility();
    updateContentVisibility();
}

// Navigation between files in "View One" mode
document.getElementById('prevBtn').addEventListener('click', function() {
    if (currentFileIndex > 0) {
        currentFileIndex--;
        showSingleFile(currentFileIndex);
    }
});

document.getElementById('nextBtn').addEventListener('click', function() {
    if (currentFileIndex < parsedData.length - 1) {
        currentFileIndex++;
        showSingleFile(currentFileIndex);
    }
});

// Update the visibility of the navigation buttons
function updateButtonVisibility() {
    const viewMode = document.querySelector('.tab-action-button.active').id;
    const navButtons = document.querySelector('.navigation-buttons');
    const activeTab = document.querySelector('.tabs .tab.active').dataset.content;

    if (activeTab === 'preview' && viewMode === 'viewOneBtn' && parsedData.length > 1) {
        navButtons.style.display = 'flex';
    } else {
        navButtons.style.display = 'none';
    }

    if (activeTab === 'preview' && hasFileData()) {
        document.querySelector('.tab-action-buttons').style.display = 'flex';
    } else {
        document.querySelector('.tab-action-buttons').style.display = 'none';
    }
}

// Add click listeners to View All and View One buttons
document.getElementById('viewAllBtn').addEventListener('click', function() {
    document.getElementById('viewOneBtn').classList.remove('active');
    this.classList.add('active');
    updateView();
    updateButtonVisibility();
});

document.getElementById('viewOneBtn').addEventListener('click', function() {
    document.getElementById('viewAllBtn').classList.remove('active');
    this.classList.add('active');
    updateView();
    updateButtonVisibility();
});

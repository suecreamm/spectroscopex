// Function to create heatmap for all data files
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

// Function to show single file's heatmap
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

// Update the visibility of the navigation buttons
function updateButtonVisibility() {
    const activeTab = document.querySelector('.tabs .tab.active').dataset.content;
    const tabActionButtons = document.querySelector('.tab-action-buttons');

    if (hasFileData() && activeTab === 'preview') {
        tabActionButtons.style.display = 'flex';
    } else {
        tabActionButtons.style.display = 'none';
    }

    const navButtons = document.querySelector('.navigation-buttons');
    const viewMode = document.querySelector('.tab-action-button.active').id;

    if (activeTab === 'preview' && viewMode === 'viewOneBtn' && parsedData.length > 1) {
        navButtons.style.display = 'flex';
    } else {
        navButtons.style.display = 'none';
    }
}

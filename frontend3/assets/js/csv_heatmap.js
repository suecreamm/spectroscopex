function createHeatmap(data) {
    const heatmapData = data.map((fileData, index) => ({
        z: fileData,
        x: fileData.map((_, idx) => idx),
        y: fileData[0].map((_, idx) => idx),
        type: 'heatmap',
        colorscale: 'Inferno',
        name: `File ${index + 1}`
    }));

    const layout = {
        title: 'CSV Data Heatmap',
        xaxis: { title: 'Index' },
        yaxis: { title: 'Columns' }
    };

    Plotly.newPlot('heatmapCanvas', heatmapData, layout);
}

function showSingleFile(index) {
    const fileData = parsedData[index];
    if (!fileData) return;

    const xValues = fileData.map((_, idx) => idx);
    const yValues = fileData[0].map((_, idx) => idx);
    const zValues = fileData;

    const heatmapData = [{
        z: zValues,
        x: xValues,
        y: yValues,
        type: 'heatmap',
        colorscale: 'Inferno'
    }];

    const layout = {
        title: `CSV Data Heatmap - File ${index + 1}`,
        xaxis: { title: 'Index' },
        yaxis: { title: 'Columns' }
    };

    Plotly.newPlot('heatmapCanvas', heatmapData, layout);
}

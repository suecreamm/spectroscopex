// 필요한 모듈 로드
const { ipcRenderer } = require('electron');
const Papa = require('papaparse');
const Plotly = require('plotly.js-dist');

// 파일 입력 요소에 이벤트 리스너 추가
document.getElementById('fileInput').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const csv = e.target.result;
            Papa.parse(csv, {
                header: false, // 데이터에 헤더가 없다고 가정
                dynamicTyping: true,
                complete: function(results) {
                    const data = results.data;
                    createHeatmap(data);
                }
            });
        };
        reader.readAsText(file);
    }
});

function createHeatmap(data) {
    const xValues = data.map((_, index) => index);
    const yValues = data[0].map((_, index) => index);
    const zValues = data;

    const heatmapData = [{
        z: zValues,
        x: xValues,
        y: yValues,
        type: 'heatmap',
        colorscale: 'Electric' 
    }];

    const layout = {
        title: 'CSV Data Heatmap',
        xaxis: { title: 'Index' },
        yaxis: { title: 'Columns' },
        autosize: true
    };

    Plotly.newPlot('heatmap', heatmapData, layout);
}

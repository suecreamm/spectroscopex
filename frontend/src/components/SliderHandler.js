export function initializeSliderHandler() {
    const xValueSlider = document.getElementById('xvalue-slider');
    const xWindowSlider = document.getElementById('xwindow-slider');
    const xValueDisplay = document.getElementById('xvalue-value');
    const xWindowDisplay = document.getElementById('xwindow-value');

    const yValueSlider = document.getElementById('yvalue-slider');
    const yWindowSlider = document.getElementById('ywindow-slider');
    const yValueDisplay = document.getElementById('yvalue-value');
    const yWindowDisplay = document.getElementById('ywindow-value');

    if (!xValueSlider || !xWindowSlider || !xValueDisplay || !xWindowDisplay ||
        !yValueSlider || !yWindowSlider || !yValueDisplay || !yWindowDisplay) {
        console.error('Slider elements not found');
        return;
    }

    xValueSlider.addEventListener('input', function() {
        xValueDisplay.textContent = xValueSlider.value;
    });

    xWindowSlider.addEventListener('input', function() {
        xWindowDisplay.textContent = xWindowSlider.value;
    });

    yValueSlider.addEventListener('input', function() {
        yValueDisplay.textContent = yValueSlider.value;
    });

    yWindowSlider.addEventListener('input', function() {
        yWindowDisplay.textContent = yWindowSlider.value;
    });
}

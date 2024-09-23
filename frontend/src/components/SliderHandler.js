export function initializeSliderHandler() {
    const xValueSlider = document.getElementById('xvalue-slider');
    const xWindowSlider = document.getElementById('xwindow-slider');
    const xValueInput = document.getElementById('xvalue-input');
    const xWindowInput = document.getElementById('xwindow-input');

    const yValueSlider = document.getElementById('yvalue-slider');
    const yWindowSlider = document.getElementById('ywindow-slider');
    const yValueInput = document.getElementById('yvalue-input');
    const yWindowInput = document.getElementById('ywindow-input');

    if (!xValueSlider || !xWindowSlider || !xValueInput || !xWindowInput ||
        !yValueSlider || !yWindowSlider || !yValueInput || !yWindowInput) {
        console.error('Slider or input elements not found');
        return;
    }

    function syncSliderAndInput(slider, input) {
        slider.addEventListener('input', function() {
            input.value = slider.value;
        });

        input.addEventListener('input', function() {
            const value = parseInt(input.value);
            if (!isNaN(value) && value >= parseInt(slider.min) && value <= parseInt(slider.max)) {
                slider.value = value;
            }
        });

        input.value = slider.value;
    }

    syncSliderAndInput(xValueSlider, xValueInput);
    syncSliderAndInput(xWindowSlider, xWindowInput);

    syncSliderAndInput(yValueSlider, yValueInput);
    syncSliderAndInput(yWindowSlider, yWindowInput);
}

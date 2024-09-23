document.addEventListener('DOMContentLoaded', function() {
    const spinner = document.getElementById('loadingSpinner');
});

function getSpinner() {
    const spinner = document.getElementById('loadingSpinner');
    if (!spinner) {
        console.error('Loading spinner element not found. Please check if the element with id "loadingSpinner" exists in the HTML.');
    }
    return spinner;
}

export function showLoadingSpinner() {
    const spinner = getSpinner();
    if (spinner) {
        spinner.classList.add('active');
    }
}

export function hideLoadingSpinner() {
    const spinner = getSpinner();
    if (spinner) {
        spinner.classList.remove('active');
    }
}

const buttons = document.querySelectorAll('button, .subtab-action-button');

export function disableButtons() {
    buttons.forEach(button => {
        button.disabled = true;
        button.classList.add('disabled');
    });
}

export function enableButtons() {
    buttons.forEach(button => {
        button.disabled = false;
        button.classList.remove('disabled');
    });
}
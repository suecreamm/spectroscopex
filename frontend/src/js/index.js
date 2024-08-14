import { initializeFileUploadHandler } from '../components/FileUploadHandler.js';
import { initializeTabs } from '../components/Tab.js';
import { initializeViewToggle } from '../components/ViewToggle.js';

document.addEventListener('DOMContentLoaded', function() {
    const fileUploadHandler = initializeFileUploadHandler();
    initializeTabs();
    initializeViewToggle();

    document.getElementById('flipUdBtn').addEventListener('click', () => {
        fileUploadHandler.sendTransformRequest('flip_ud');
    });
    document.getElementById('flipLrBtn').addEventListener('click', () => {
        fileUploadHandler.sendTransformRequest('flip_lr');
    });
    document.getElementById('rotateCcw90Btn').addEventListener('click', () => {
        fileUploadHandler.sendTransformRequest('rotate_ccw90');
    });
    document.getElementById('rotateCw90Btn').addEventListener('click', () => {
        fileUploadHandler.sendTransformRequest('rotate_cw90');
    });
    document.getElementById('resetBtn').addEventListener('click', () => {
        fileUploadHandler.sendTransformRequest('reset');
    });
});

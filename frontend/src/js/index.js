import { initializeFileUploadHandler } from '../components/FileUploadHandler.js';
import { initializeTabs } from '../components/Tab.js';
import { initializeViewToggle } from '../components/ViewToggle.js';
import { initializeTransform } from '../components/Transform.js';

document.addEventListener('DOMContentLoaded', function() {
    const fileUploadHandler = initializeFileUploadHandler();
    initializeTransform(fileUploadHandler);
    initializeTabs();
    initializeViewToggle();
});
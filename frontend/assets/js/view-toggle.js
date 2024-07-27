document.addEventListener('DOMContentLoaded', () => {
    function updateSubTabs() {
        const activeTab = document.querySelector('.tabs .tab.active');
        const tabContentId = activeTab ? activeTab.dataset.content : null;

        document.querySelectorAll('.subtab-action-buttons, .content').forEach(element => {
            if (element.closest('.content').id === tabContentId && hasFileData()) {
                element.style.display = 'flex';
            } else {
                element.style.display = 'none';
            }
        });
    }

    updateSubTabs();

    document.querySelectorAll('.tabs .tab').forEach(tab => {
        tab.addEventListener('click', updateSubTabs);
    });

    // Other event listeners for buttons remain unchanged
});

document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.tabs .tab');
    const contents = document.querySelectorAll('.content');

    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const target = tab.getAttribute('data-content');

            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            document.getElementById(target).classList.add('active');

            if (typeof updateButtonVisibility === 'function') {
                updateButtonVisibility();
            }
            if (typeof updateContentVisibility === 'function') {
                updateContentVisibility();
            }
        });
    });

    // Initially hide all content sections except the first one
    updateContentVisibility();

    // Define the updateContentVisibility function to manage content visibility
    function updateContentVisibility() {
        const activeTab = document.querySelector('.tabs .tab.active');
        const target = activeTab ? activeTab.getAttribute('data-content') : null;

        const contents = document.querySelectorAll('.content');
        contents.forEach(content => {
            if (content.id === target) {
                content.classList.add('active');
            } else {
                content.classList.remove('active');
            }
        });
}
});

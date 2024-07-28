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
});

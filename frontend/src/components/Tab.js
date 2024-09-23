export function initializeTabs() {
  const tabs = document.querySelectorAll('.tabs .tab');
  const tabPanels = document.querySelectorAll('.tabPanel');

  tabs.forEach(tab => {
    tab.addEventListener('click', function() {
      const target = tab.getAttribute('data-content');

      tabs.forEach(t => t.classList.remove('active'));
      tabPanels.forEach(panel => {
        panel.classList.remove('active');
        panel.style.display = 'none';
      });

      tab.classList.add('active');
      const targetPanel = document.getElementById(target);
      targetPanel.classList.add('active');
      targetPanel.style.display = 'block';

      if (typeof updateButtonVisibility === 'function') {
        updateButtonVisibility();
      }
    });
  });

  // Initially hide all content sections except the first one
  updateContentVisibility();
}

function updateContentVisibility() {
  const activeTab = document.querySelector('.tabs .tab.active');
  const target = activeTab ? activeTab.getAttribute('data-content') : null;

  document.querySelectorAll('.tabPanel').forEach(panel => {
    if (panel.id === target) {
      panel.classList.add('active');
      panel.style.display = 'block';
    } else {
      panel.classList.remove('active');
      panel.style.display = 'none';
    }
  });
}

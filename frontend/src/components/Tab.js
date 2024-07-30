export function initializeTabs() {
    const tabs = document.querySelectorAll('.tabs .tab');
    const contents = document.querySelectorAll('.content');
  
    tabs.forEach(tab => {
      tab.addEventListener('click', function() {
        const target = tab.getAttribute('data-content');
  
        tabs.forEach(t => t.classList.remove('active'));
        contents.forEach(c => {
          c.classList.remove('active');
          c.style.display = 'none';
        });
  
        tab.classList.add('active');
        const targetContent = document.getElementById(target);
        targetContent.classList.add('active');
        targetContent.style.display = 'block';
  
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
  
    document.querySelectorAll('.content').forEach(content => {
      if (content.id === target) {
        content.classList.add('active');
        content.style.display = 'block';
      } else {
        content.classList.remove('active');
        content.style.display = 'none';
      }
    });
  }
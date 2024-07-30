export function initializeViewToggle() {
    try {
        function updateSubTabs() {
            const activeTab = document.querySelector('.tabs .tab.active');
            const tabContentId = activeTab ? activeTab.dataset.content : null;

            document.querySelectorAll('.content').forEach(content => {
                if (content.id === tabContentId && hasFileData()) {
                    content.style.display = 'block';
                    content.querySelectorAll('.subtab-action-buttons').forEach(button => {
                        button.style.display = 'flex';
                    });
                } else {
                    content.style.display = 'none';
                }
            });
        }

        // 초기 상태 업데이트
        updateSubTabs();

        // 탭 클릭 이벤트 설정
        const tabs = document.querySelectorAll('.tabs .tab');
        if (tabs.length > 0) {
            tabs.forEach(tab => {
                tab.addEventListener('click', updateSubTabs);
            });
        } else {
            console.warn("No elements found with class '.tabs .tab'");
        }

        function hasFileData() {
            const fileInput = document.getElementById('fileInput');
            return fileInput && fileInput.files.length > 0;
        }

        // View All 및 View One 버튼 기능 추가
        const viewAllButton = document.getElementById('viewAllBtn');
        const viewSingleButton = document.getElementById('viewSingleBtn');

        if (viewAllButton) {
            viewAllButton.addEventListener('click', () => switchViewMode('all'));
        } else {
            console.warn("Element with id 'viewAllBtn' not found");
        }

        if (viewSingleButton) {
            viewSingleButton.addEventListener('click', () => switchViewMode('one'));
        } else {
            console.warn("Element with id 'viewSingleBtn' not found");
        }

        function switchViewMode(view) {
            if (viewAllButton && viewSingleButton) {
                if (view === 'all') {
                    viewAllButton.classList.add('active');
                    viewSingleButton.classList.remove('active');
                    // 추가 로직: 모든 항목 표시
                } else {
                    viewSingleButton.classList.add('active');
                    viewAllButton.classList.remove('active');
                    // 추가 로직: 단일 항목 표시
                }
                updateSubTabs();
            } else {
                console.warn("View mode buttons not found");
            }
        }
    } catch (error) {
        console.error("Error initializing view toggle:", error);
    }
}
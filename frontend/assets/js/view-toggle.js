document.addEventListener('DOMContentLoaded', () => {
    function updateSubTabs() {
        const activeTab = document.querySelector('.tabs .tab.active');
        const tabContentId = activeTab ? activeTab.dataset.content : null;

        document.querySelectorAll('.content').forEach(content => {
            if (content.id === tabContentId && hasFileData()) {
                content.style.display = 'block'; // 필요한 경우 'flex' 또는 다른 스타일로 변경
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
    document.querySelectorAll('.tabs .tab').forEach(tab => {
        tab.addEventListener('click', updateSubTabs);
    });

    function hasFileData() {
        const fileInput = document.getElementById('fileInput');
        return fileInput && fileInput.files.length > 0;
    }
});

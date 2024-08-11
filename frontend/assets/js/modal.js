// Function to load content into the modal
function loadModalContent(contentUrl) {
    fetch(contentUrl)
    .then(response => response.text())
    .then(data => {
        // license.html의 내용을 modalBodyContent에 삽입
        let modalContent = document.getElementById("modalBodyContent");
        if (modalContent) {
            modalContent.innerHTML = data;
        }

        // 모달을 표시
        let modal = document.getElementById("licenseModal");
        if (modal) {
            modal.style.display = "block";

            // 닫기 버튼 이벤트 설정
            var closeButton = modal.querySelector(".close");
            if (closeButton) {
                closeButton.onclick = function() {
                    modal.style.display = "none";
                };
            }

            // 모달 외부를 클릭했을 때 모달 닫기
            window.onclick = function(event) {
                if (event.target == modal) {
                    modal.style.display = "none";
                }
            };
        }
    })
    .catch(error => {
        console.error('Error loading content:', error);
    });
}

// 모든 data-modal 속성을 가진 요소에 이벤트 리스너를 설정
document.querySelectorAll("[data-modal]").forEach(function(element) {
    element.addEventListener("click", function(event) {
        event.preventDefault();
        const contentUrl = element.getAttribute("data-modal");
        loadModalContent(contentUrl);
    });
});

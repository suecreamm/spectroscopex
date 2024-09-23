export function showModalMessage(message) {
    let modalElement = document.getElementById('messageModal');
    
    if (!modalElement) {
        const modalTemplate = `
            <div id="messageModal" class="modal">
                <div class="modal-content">
                    <span class="close">&times;</span>
                    <p id="modalMessageContent"></p>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalTemplate);
        modalElement = document.getElementById('messageModal');

        const closeButton = modalElement.querySelector('.close');
        closeButton.onclick = function() {
            modalElement.style.display = "none";
        };

        window.onclick = function(event) {
            if (event.target == modalElement) {
                modalElement.style.display = "none";
            }
        };
    }

    const modalMessageContent = document.getElementById('modalMessageContent');
    modalMessageContent.textContent = message;
    modalElement.style.display = "block";
}

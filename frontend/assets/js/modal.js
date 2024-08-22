const modals = [
    { modalId: 'licenseModal', contentFile: 'license.html' },
    { modalId: 'aboutModal', contentFile: 'about.html' },
    { modalId: 'supportModal', contentFile: 'support.html' },
    { modalId: 'commandModal', contentFile: 'command.html' },
];

modals.forEach(({ modalId, contentFile }) => {
    const modalTemplate = `
        <div id="${modalId}" class="modal">
            <div class="modal-content">
                <!-- ${contentFile} -->
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalTemplate);
});


function loadModalContent(modalId, contentUrl) {
    fetch(contentUrl)
    .then(response => response.text())
    .then(data => {
        let modalContent = document.querySelector(`#${modalId} .modal-content`);
        if (modalContent) {
            modalContent.innerHTML = data;
        }

        let modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = "block";

            // Close event for the close button
            var closeButton = modal.querySelector(".close");
            if (closeButton) {
                closeButton.onclick = function() {
                    modal.style.display = "none";
                    window.removeEventListener('click', outsideClickListener);
                };
            }

            // Function to close modal when clicking outside of it
            function outsideClickListener(event) {
                if (event.target == modal) {
                    modal.style.display = "none";
                    window.removeEventListener('click', outsideClickListener);
                }
            }

            // Add the event listener to detect clicks outside the modal
            window.addEventListener('click', outsideClickListener);
        }
    })
    .catch(error => {
        console.error('Error loading content:', error);
    });
}

// Attach event listeners to elements with the [data-modal] attribute
document.querySelectorAll("[data-modal]").forEach(function(element) {
    element.addEventListener("click", function(event) {
        event.preventDefault();
        const contentUrl = element.getAttribute("data-modal");
        const modalId = element.getAttribute("data-target-modal") || "licenseModal";
        loadModalContent(modalId, contentUrl);
    });
});

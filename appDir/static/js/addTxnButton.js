var modal = document.querySelector("#add-txn-modal");
var trigger = document.querySelector("#add-txn-button");
var closeButton = document.querySelector("#add-txn-modal-close");

function toggleModal() {
    modal.classList.toggle("show-modal");
}

trigger.addEventListener("click", toggleModal);
closeButton.addEventListener("click", toggleModal);
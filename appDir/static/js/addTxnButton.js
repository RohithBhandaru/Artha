var modal = document.querySelector("#add-txn-modal");
var trigger = document.querySelector("#add-txn-button");
var closeButton = document.querySelector("#add-txn-modal-close");

function toggleAddTxnModal() {
    modal.classList.toggle("show-modal");
}

trigger.addEventListener("click", toggleAddTxnModal);
closeButton.addEventListener("click", toggleAddTxnModal);
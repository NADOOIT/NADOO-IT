function closeModal() {
	var container = document.getElementById("modals-here")
	var backdrop = document.getElementById("modal-backdrop")
	var modal = document.getElementById("modal")
	var modalform = document.getElementById("modal-form")

	modal.classList.remove("show")
	backdrop.classList.remove("show")

	setTimeout(function() {
		container.removeChild(modalform)
	/* 	container.removeChild(backdrop)
		container.removeChild(modal) */

	}, 200)
}
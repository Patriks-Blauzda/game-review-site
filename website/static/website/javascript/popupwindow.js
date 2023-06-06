function displayModal() {
  document.getElementById("report-popup").style.display = "block";
}

// When the user clicks on <span> (x), close the modal
function closeModal() {
  document.getElementById("report-popup").style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == document.getElementById("myModal")) {
    document.getElementById("report-popup").style.display = "none";
  }
} 
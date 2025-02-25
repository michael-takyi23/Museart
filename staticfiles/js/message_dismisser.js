document.addEventListener("DOMContentLoaded", function () {
    // Find all dismissable messages
    const dismissButtons = document.querySelectorAll(".dismiss-message");

    dismissButtons.forEach(button => {
        button.addEventListener("click", function () {
            this.parentElement.style.display = "none"; // Hide the message
        });
    });

    // Auto-dismiss messages after 5 seconds
    setTimeout(() => {
        document.querySelectorAll(".alert").forEach(alert => {
            alert.style.display = "none";
        });
    }, 5000);
});

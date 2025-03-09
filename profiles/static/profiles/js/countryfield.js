document.addEventListener("DOMContentLoaded", function () {
    const countrySelect = document.getElementById("id_default_country");

    // Function to update the color based on selection
    function updateCountryColor() {
        if (!countrySelect.value) {
            countrySelect.style.color = "#aab7c4";  // Placeholder color
        } else {
            countrySelect.style.color = "#000";  // Default text color
        }
    }

    // Run function on page load
    updateCountryColor();

    // Listen for changes in selection
    countrySelect.addEventListener("change", updateCountryColor);
});

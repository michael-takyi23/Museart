document.addEventListener('DOMContentLoaded', function () {
    // Function to trigger a specific toast by its ID
    function showToast(toastId) {
        var toastEl = document.getElementById(toastId);
        if (toastEl) {
            var toast = new bootstrap.Toast(toastEl);
            toast.show();
        } else {
            console.error(`Toast with ID "${toastId}" not found.`);
        }
    }

    // Add to Cart Toast
    const addToCartBtn = document.getElementById('addToCartBtn');
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', function () {
            showToast('addToCartToast');
        });
    }

    // Remove from Cart Toasts
    document.querySelectorAll('.remove-item').forEach(btn => {
        btn.addEventListener('click', function () {
            showToast('removeFromCartToast');
        });
    });

    // Order Confirmation Toast
    const confirmOrderBtn = document.getElementById('confirmOrderBtn');
    if (confirmOrderBtn) {
        confirmOrderBtn.addEventListener('click', function () {
            showToast('orderConfirmationToast');
        });
    }

    // Error Toast Function
    function showErrorToast() {
        showToast('errorToast');
    }

    // Example: Call showErrorToast() on an error scenario
    // Example: Uncomment the next line to simulate an error toast trigger
    // showErrorToast();
});

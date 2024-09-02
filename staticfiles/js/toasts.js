document.addEventListener('DOMContentLoaded', function () {
    // Function to trigger a specific toast by its ID
    function showToast(toastId) {
        var toastEl = document.getElementById(toastId);
        var toast = new bootstrap.Toast(toastEl);
        toast.show();
    }
    
    // Add to Cart Toast
    const addToCartBtn = document.getElementById('addToCartBtn');
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', function () {
            var toastEl = document.getElementById('addToCartToast');
            var toast = new bootstrap.Toast(toastEl);
            toast.show();
        });
    }

    // Remove from Cart Toast
    const removeItemBtns = document.querySelectorAll('.remove-item');
    removeItemBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            var toastEl = document.getElementById('removeFromCartToast');
            var toast = new bootstrap.Toast(toastEl);
            toast.show();
        });
    });

    // Order Confirmation Toast
    const confirmOrderBtn = document.getElementById('confirmOrderBtn');
    if (confirmOrderBtn) {
        confirmOrderBtn.addEventListener('click', function () {
            var toastEl = document.getElementById('orderConfirmationToast');
            var toast = new bootstrap.Toast(toastEl);
            toast.show();
        });
    }

    // Error Toast (for example during a network issue or failed action)
    function showErrorToast() {
        var toastEl = document.getElementById('errorToast');
        var toast = new bootstrap.Toast(toastEl);
        toast.show();
    }

    // Example: Call showErrorToast() on an error scenario
});

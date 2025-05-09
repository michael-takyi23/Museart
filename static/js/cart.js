console.log("✅ cart.js is running...");

document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ DOMContentLoaded event fired! JavaScript is running.");

    // Attach event listeners to update and remove buttons
    document.querySelectorAll(".update-cart").forEach(button => {
        button.addEventListener("click", function () {
            console.log("✅ Update button clicked!");
            const itemId = this.dataset.itemId;
            const quantityInput = document.querySelector(`.quantity-input[data-item-id="${itemId}"]`);
            const quantity = parseInt(quantityInput.value);

            if (quantity > 0) {
                updateCart(itemId, quantity);
            } else {
                alert('Quantity must be greater than zero.');
            }
        });
    });

    document.querySelectorAll(".remove-item").forEach(button => {
        console.log("🗑 Found remove button:", button);
        button.addEventListener("click", function () {
            console.log("✅ Remove button clicked!");
            const itemId = this.dataset.itemId;
            removeFromCart(itemId);
        });
    });

    // Update Cart Function
    function updateCart(itemId, quantity) {
        console.log(`📡 Sending update request for item ${itemId}, quantity: ${quantity}`);

        fetch(`/cart/update/${itemId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({ quantity }),
        })
        .then(response => response.json())
        .then(data => {
            console.log("✅ Server Response:", data);
            if (data.error) {
                alert(data.error);
            } else {
                // Update UI dynamically without page reload
                document.querySelector(`.subtotal[data-item-id="${itemId}"]`).innerText = `€${data.item_subtotal.toFixed(2)}`;
                document.querySelector('.cart-total').innerText = `€${data.cart_total.toFixed(2)}`;
            }
        })
        .catch(error => {
            console.error("❌ Error updating cart:", error);
            alert('Failed to update cart. Please try again.');
        });
    }

    // Remove Item Function
    function removeFromCart(itemId) {
        console.log(`📡 Sending remove request for item ${itemId}`);

        fetch(`/cart/remove/${itemId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
        })
        .then(response => response.json())
        .then(data => {
            console.log("✅ Server Response:", data);
            if (data.error) {
                alert(data.error);
            } else {
                // Remove the item's row dynamically
                const itemRow = document.querySelector(`.cart-item[data-item-id="${itemId}"]`);
                if (itemRow) {
                    itemRow.remove();
                }
                // Update cart total dynamically
                document.querySelector('.cart-total').innerText = `€${data.cart_total.toFixed(2)}`;
            }
        })
        .catch(error => {
            console.error("❌ Error removing item:", error);
            alert('Failed to remove item. Please try again.');
        });
    }

    // Helper function to get CSRF token
    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.content || '';
    }
});
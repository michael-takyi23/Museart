console.log("✅ cart.js is running from file...");
alert("✅ cart.js is executing!");

document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ DOMContentLoaded event fired! JavaScript is running.");
    alert("✅ JavaScript is executing after page load!");
});

    // Ensure buttons exist before adding event listeners
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
                document.querySelector(`.subtotal[data-item-id="${itemId}"]`).innerText = `€${data.item_subtotal.toFixed(2)}`;
                document.querySelector('.cart-total').innerText = `€${data.cart_total.toFixed(2)}`;
                setTimeout(() => location.reload(), 500);
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
                document.querySelector(`.cart-item[data-item-id="${itemId}"]`).remove();
                document.querySelector('.cart-total').innerText = `€${data.cart_total.toFixed(2)}`;
                setTimeout(() => location.reload(), 5000);
            }
        })
        .catch(error => {
            console.error("❌ Error removing item:", error);
            alert('Failed to remove item. Please try again.');
        });
    }

    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.content || '';
    }
});

console.log("✅ cart.js is running...");

document.addEventListener('DOMContentLoaded', function () {
    console.log("✅ DOM is fully loaded");

    document.querySelectorAll(".update-cart").forEach(button => {
        console.log("🔄 Found update button:", button); // ✅ Log all buttons found
        button.addEventListener("click", function () {
            console.log("✅ Update button clicked for item:", this.dataset.itemId);
        });
    });

    document.querySelectorAll(".remove-item").forEach(button => {
        console.log("🗑 Found remove button:", button); // ✅ Log all buttons found
        button.addEventListener("click", function () {
            console.log("✅ Remove button clicked for item:", this.dataset.itemId);
        });
    });
});


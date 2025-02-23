document.addEventListener('DOMContentLoaded', function () {
    // Event Delegation for Update and Remove Buttons
    document.addEventListener('click', function (event) {
        // Update Cart Quantity
        if (event.target.classList.contains('update-cart')) {
            const itemId = event.target.dataset.itemId;
            const quantityInput = document.querySelector(`.quantity-input[data-item-id="${itemId}"]`);
            const quantity = parseInt(quantityInput.value);

            if (quantity > 0) {
                updateCart(itemId, quantity);
            } else {
                alert('Quantity must be greater than zero.');
            }
        }

        // Remove Item from Cart
        if (event.target.classList.contains('remove-item')) {
            const itemId = event.target.dataset.itemId;
            removeFromCart(itemId);
        }
    });

    // Update Cart Function
    function updateCart(itemId, quantity) {
        fetch(`/cart/update/${itemId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({ quantity }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to update cart.');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                // Update Subtotal and Total dynamically
                document.querySelector(`.subtotal[data-item-id="${itemId}"]`).innerText = `€${data.item_subtotal.toFixed(2)}`;
                document.querySelector('.cart-total').innerText = `€${data.cart_total.toFixed(2)}`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to update cart. Please try again.');
        });
    }

    // Remove Item Function
    function removeFromCart(itemId) {
        fetch(`/cart/remove/${itemId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to remove item.');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                // Remove the item's row dynamically
                const itemRow = document.querySelector(`.cart-item[data-item-id="${itemId}"]`);
                if (itemRow) {
                    itemRow.remove();
                }
                // Update the cart total dynamically
                document.querySelector('.cart-total').innerText = `€${data.cart_total.toFixed(2)}`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to remove item. Please try again.');
        });
    }

    // Helper function to get CSRF token
    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.content || '';
    }
});

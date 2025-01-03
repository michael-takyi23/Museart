document.addEventListener('DOMContentLoaded', function () {
    // Update cart item quantity
    const updateButtons = document.querySelectorAll('.update-cart');
    updateButtons.forEach(button => {
        button.addEventListener('click', function () {
            const itemId = this.dataset.itemId;
            const quantityInput = document.querySelector(`.quantity-input[data-item-id="${itemId}"]`);
            const quantity = parseInt(quantityInput.value);

            if (quantity > 0) {
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
                    if (data.error) {
                        alert(data.error);
                    } else {
                        // Update subtotal and total dynamically
                        document.querySelector(`.subtotal[data-item-id="${itemId}"]`).innerText = `€${data.item_subtotal.toFixed(2)}`;
                        document.querySelector('.cart-total').innerText = `€${data.cart_total.toFixed(2)}`;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Failed to update cart. Please try again.');
                });
            } else {
                alert('Quantity must be greater than zero.');
            }
        });
    });

    // Remove item from cart
    const removeButtons = document.querySelectorAll('.remove-item');
    removeButtons.forEach(button => {
        button.addEventListener('click', function () {
            const itemId = this.dataset.itemId;

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
                return response.json(); // Parse JSON response
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
        });
    });

    // Helper function to get CSRF token
    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
});

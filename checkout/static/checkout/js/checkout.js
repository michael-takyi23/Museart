

document.addEventListener("DOMContentLoaded", function () {
    console.log("🔄 Initializing Stripe Checkout...");

    const stripePublicKey = JSON.parse(document.getElementById('id_stripe_public_key').textContent);
    const clientSecret = JSON.parse(document.getElementById('id_client_secret').textContent);

    if (!stripePublicKey || !clientSecret) {
        alert("Error setting up payment. Please refresh and try again.");
        return;
    }

    // Initialize Stripe
    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements({ clientSecret });

    const paymentElement = elements.create('payment');
    paymentElement.mount('#payment-element');

    console.log("✅ Stripe initialized successfully.");
});

function handlePaymentForm(stripe, elements, clientSecret) {
    const form = document.getElementById('payment-form');
    const loadingOverlay = document.getElementById('payment-overlay');
    const errorContainer = document.getElementById('card-errors');
    const submitButton = document.getElementById('submit');

    if (!form || !submitButton || !loadingOverlay) {
        console.warn("⚠️ Missing required DOM elements.");
        return;
    }

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Prevent multiple submissions
        if (submitButton.disabled) return;

        console.log("💳 Submitting payment form...");
        loadingOverlay.classList.remove("d-none");
        submitButton.disabled = true;
        errorContainer.textContent = "";

        try {
            // ✅ Cache checkout data before processing payment
            await cacheCheckoutData(clientSecret);

            // ✅ Confirm the payment
            const { error, paymentIntent } = await stripe.confirmPayment({
                elements,
                confirmParams: {
                    return_url: window.location.href,
                },
                redirect: "if_required",
            });

            if (error) {
                console.error("❌ Payment error:", error.message);
                errorContainer.innerHTML = `
                    <span class="icon" role="alert">
                        <i class="fas fa-times"></i>
                    </span>
                    <span>${error.message}</span>`;
                loadingOverlay.classList.add("d-none");
                submitButton.disabled = false;
                return;
            }

            console.log("✅ Payment confirmed. Polling order status...");
            pollOrderStatus(paymentIntent.id);
        } catch (err) {
            console.error("❌ Unexpected error during payment:", err);
            errorContainer.textContent = "Something went wrong. Please try again.";
            loadingOverlay.classList.add("d-none");
            submitButton.disabled = false;
        }
    });
}

// ✅ Cache checkout data before processing payment
async function cacheCheckoutData(clientSecret) {
    const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;
    const saveInfo = document.getElementById('id-save-info')?.checked;
    const postData = {
        csrfmiddlewaretoken: csrfToken,
        client_secret: clientSecret,
        save_info: saveInfo,
    };

    try {
        const response = await fetch("/checkout/cache_checkout_data/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams(postData),
        });

        if (!response.ok) {
            throw new Error("Failed to cache checkout data.");
        }
        console.log("✅ Checkout data cached successfully.");
    } catch (err) {
        console.error("⚠️ Error caching checkout data:", err);
        alert("There was an issue saving your checkout data. Please try again.");
        location.reload(); // Fallback to Django messages
    }
}

// ✅ Poll order status until confirmed, then redirect
function pollOrderStatus(paymentIntentId, attempt = 1, maxAttempts = 30, delay = 1000) {
    if (attempt > maxAttempts) {
        alert("⚠️ Your order is still processing. Please check your email or contact support.");
        console.error("🚨 Order not found after max retries.");
        return;
    }

    console.log(`⏳ Polling for order... Attempt ${attempt}/${maxAttempts}`);

    fetch(`/checkout/get-order-number/?payment_intent=${paymentIntentId}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                console.log("🎉 Order found! Redirecting to success page...");
                window.location.href = data.redirect_url;
            } else {
                setTimeout(() => {
                    pollOrderStatus(paymentIntentId, attempt + 1, maxAttempts, delay);
                }, delay);
            }
        })
        .catch(err => {
            console.error("⚠️ Polling failed:", err);
            setTimeout(() => {
                pollOrderStatus(paymentIntentId, attempt + 1, maxAttempts, delay);
            }, delay);
        });
}

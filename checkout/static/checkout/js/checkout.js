document.addEventListener("DOMContentLoaded", async function () {
    console.log("🔄 Initializing Stripe Checkout...");

    const stripePublicKey = JSON.parse(document.getElementById('id_stripe_public_key')?.textContent || '""');
    const clientSecret = JSON.parse(document.getElementById('id_client_secret')?.textContent || '""');

    console.log("🔍 Stripe Key:", stripePublicKey);
    console.log("🔍 Client Secret:", clientSecret);

    if (!stripePublicKey || !clientSecret) {
        alert("Checkout setup failed. Please refresh the page.");
        return;
    }

    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements({ clientSecret });

    const paymentElement = elements.create('payment');
    paymentElement.mount('#payment-element');

    const form = document.getElementById('payment-form');
    const loadingOverlay = document.getElementById('payment-overlay');
    const errorContainer = document.getElementById('card-errors');
    const submitButton = document.getElementById('submit');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Spinner ON
        loadingOverlay.classList.remove('d-none');
        submitButton.disabled = true;
        errorContainer.textContent = "";

        // Cache checkout data to webhook
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

            if (!response.ok) throw new Error("Failed to cache checkout data");
        } catch (err) {
            console.error("⚠️ Error caching checkout data:", err);
            location.reload(); // fallback to Django messages
        }

        // Confirm the payment
        try {
            const { error, paymentIntent } = await stripe.confirmPayment({
                elements,
                confirmParams: {
                    return_url: window.location.href,
                },
                redirect: "if_required",
            });

            if (error) {
                console.error("❌ Stripe payment error:", error.message);
                errorContainer.innerHTML = `
                    <span class="icon" role="alert">
                        <i class="fas fa-times"></i>
                    </span>
                    <span>${error.message}</span>`;
                loadingOverlay.classList.add('d-none');
                submitButton.disabled = false;
                return;
            }

            // Fallback: poll until order is saved, then redirect
            console.log("✅ Payment confirmed. Starting polling...");
            pollOrderStatus(paymentIntent.id);

        } catch (err) {
            console.error("❌ Stripe JS fatal error:", err);
            errorContainer.textContent = "Something went wrong. Please try again.";
            loadingOverlay.classList.add('d-none');
            submitButton.disabled = false;
        }
    });
});

function pollOrderStatus(paymentIntentId, attempt = 1, maxAttempts = 30, delay = 1000) {
    if (attempt > maxAttempts) {
        alert("⚠️ Order is still processing. Please check your email or contact support.");
        return;
    }

    fetch(`/checkout/get-order-number/?payment_intent=${paymentIntentId}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                console.log("🎉 Order found! Redirecting...");
                window.location.href = data.redirect_url;
            } else {
                setTimeout(() => {
                    pollOrderStatus(paymentIntentId, attempt + 1, maxAttempts, delay);
                }, delay);
            }
        })
        .catch((err) => {
            console.error("⛔ Polling error:", err);
            setTimeout(() => {
                pollOrderStatus(paymentIntentId, attempt + 1, maxAttempts, delay);
            }, delay);
        });
}

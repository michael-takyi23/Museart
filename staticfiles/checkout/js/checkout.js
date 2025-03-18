document.addEventListener("DOMContentLoaded", async function () {
    const stripePublicKeyElement = document.getElementById('id_stripe_public_key');
    const clientSecretElement = document.getElementById('id_client_secret');

    if (!stripePublicKeyElement || !clientSecretElement) {
        console.error("🚨 Missing Stripe keys in the DOM.");
        return;
    }

    const stripePublicKey = stripePublicKeyElement.textContent.trim();
    const clientSecret = clientSecretElement.textContent.trim();

    // ✅ Remove client secret from the DOM for security reasons
    clientSecretElement.textContent = "";

    if (!stripePublicKey || !clientSecret) {
        console.error("🚨 Stripe credentials are missing!");
        document.getElementById('card-errors').textContent = "Error: Unable to process payment.";
        return;
    }

    let stripe;
    try {
        stripe = Stripe(stripePublicKey);
    } catch (err) {
        console.error("🚨 Failed to initialize Stripe:", err);
        return;
    }

    const elements = stripe.elements({ clientSecret });
    const paymentElement = elements.create('payment');

    const paymentContainer = document.getElementById('payment-element');
    if (!paymentContainer) {
        console.error("🚨 Payment container not found.");
        return;
    }
    paymentElement.mount('#payment-element');

    const form = document.getElementById('payment-form');
    const loadingSpinner = document.getElementById('payment-overlay');
    const errorContainer = document.getElementById('card-errors');
    const submitButton = form?.querySelector('button[type="submit"]');

    if (!form || !submitButton) {
        console.error("🚨 Form or submit button is missing.");
        return;
    }

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        
        // ✅ Add loading indicator and disable the button
        submitButton.disabled = true;
        submitButton.textContent = "Processing...";
        if (loadingSpinner) loadingSpinner.classList.remove("d-none");
        errorContainer.textContent = "";

        try {
            const { error, paymentIntent } = await stripe.confirmPayment({
                elements,
                confirmParams: {
                    return_url: window.location.origin + "/checkout/get-order-number/",
                },
            });

            if (error) {
                console.error("🚨 Stripe Payment Error:", error.message);
                errorContainer.textContent = "Payment failed: " + error.message;
            } else if (paymentIntent?.status === 'succeeded') {
                console.log("✅ Payment successful! Redirecting...");
                window.location.href = `/checkout/get-order-number/?payment_intent=${paymentIntent.id}`;
            } else {
                errorContainer.textContent = "Payment processing error. Please try again.";
            }
        } catch (err) {
            console.error("🚨 Unexpected Error:", err);
            errorContainer.textContent = 'An unexpected error occurred. Please try again.';
        } finally {
            // ✅ Restore button state
            submitButton.disabled = false;
            submitButton.textContent = "Pay";
            if (loadingSpinner) loadingSpinner.classList.add("d-none");
        }
    });

    // ✅ Auto-check if a payment was already completed after a redirect
    const queryClientSecret = new URLSearchParams(window.location.search).get('payment_intent_client_secret');
    if (queryClientSecret) {
        console.log("🔄 Checking previous payment intent...");
        try {
            const { paymentIntent } = await stripe.retrievePaymentIntent(queryClientSecret);
            if (paymentIntent?.status === 'succeeded') {
                console.log("✅ Payment was successful! Redirecting...");
                window.location.href = `/checkout/get-order-number/?payment_intent=${paymentIntent.id}`;
            }
        } catch (err) {
            console.error("🚨 Error retrieving payment intent:", err);
        }
    }
});

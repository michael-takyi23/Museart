document.addEventListener("DOMContentLoaded", async function () {
    const stripePublicKey = document.getElementById('id_stripe_public_key')?.textContent.trim();
    const clientSecret = document.getElementById('id_client_secret')?.textContent.trim();

    console.log("Stripe Public Key:", stripePublicKey);
    console.log("Client Secret:", clientSecret);

    if (!stripePublicKey) {
        console.error("🚨 Stripe public key is missing!");
        return;
    }

    if (!clientSecret) {
        console.error("🚨 Client secret is missing! Payment Intent may not have been created.");
        const errorContainer = document.getElementById('card-errors');
        if (errorContainer) errorContainer.textContent = "Error: Payment cannot be processed.";
        return;
    }

    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements({ clientSecret: clientSecret });

    console.log("🎯 Mounting Stripe Elements...");
    const paymentElement = elements.create('payment');
    paymentElement.mount('#payment-element');

    const form = document.getElementById('payment-form');
    const loadingSpinner = document.getElementById('payment-overlay');
    const errorContainer = document.getElementById('card-errors');
    const submitButton = form.querySelector('button[type="submit"]');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        console.log("🛒 Processing payment...");

        if (loadingSpinner) loadingSpinner.classList.remove("d-none");
        submitButton.disabled = true;
        if (errorContainer) errorContainer.textContent = "";

        try {
            console.log("⚡ Sending request to Stripe for payment confirmation...");
            const { error, paymentIntent } = await stripe.confirmPayment({
                elements,
                confirmParams: {
                    return_url: window.location.origin + "/checkout/get-order-number/",
                },
            });

            if (error) {
                console.error("🚨 Stripe Payment Error:", error.message);
                errorContainer.textContent = "Payment failed: " + error.message;
            } else if (paymentIntent) {
                console.log("✅ Payment Intent Received:", paymentIntent);
                if (paymentIntent.status === 'succeeded') {
                    console.log("✅ Payment successful! Redirecting...");
                    window.location.href = "/checkout/get-order-number/?payment_intent=" + paymentIntent.id;
                } else {
                    errorContainer.textContent = "Payment processing error. Please try again.";
                }
            }
        } catch (err) {
            console.error("🚨 Unexpected Error:", err);
            errorContainer.textContent = 'An unexpected error occurred. Please try again.';
        } finally {
            submitButton.disabled = false;
            if (loadingSpinner) loadingSpinner.classList.add("d-none");
        }
    });

    // ✅ Check if payment was already completed (in case of redirect)
    const queryClientSecret = new URLSearchParams(window.location.search).get('payment_intent_client_secret');
    if (queryClientSecret) {
        console.log("🔄 Checking previous payment intent...");
        stripe.retrievePaymentIntent(queryClientSecret).then(({ paymentIntent }) => {
            if (paymentIntent) {
                console.log("💳 Payment Intent Retrieved:", paymentIntent);
                if (paymentIntent.status === 'succeeded') {
                    console.log("✅ Payment was successful! Redirecting...");
                    window.location.href = "/checkout/get-order-number/?payment_intent=" + paymentIntent.id;
                }
            }
        }).catch((err) => {
            console.error("🚨 Error retrieving payment intent:", err);
        });
    }
});

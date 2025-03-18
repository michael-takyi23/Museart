document.addEventListener("DOMContentLoaded", async function () {
    console.log("🔄 Initializing Stripe Checkout...");

    // ✅ Fetch order number from hidden div
    const orderDataDiv = document.getElementById("order-data");
    const orderNumber = orderDataDiv ? orderDataDiv.getAttribute("data-order-number") : null;

    if (!orderNumber) {
        console.error("🚨 ERROR: Order number is missing! Checkout cannot proceed.");
        alert("An error occurred. Please refresh and try again.");
        return;
    }

    console.log("🛒 Order Number Retrieved:", orderNumber);

    // ✅ Fetch Stripe public key & client secret from Django template
    const stripePublicKey = document.getElementById('id_stripe_public_key')?.textContent.trim();
    const stripeDataDiv = document.querySelector("#stripe-data");

    // ✅ Ensure `client_secret` is correctly retrieved
    const clientSecret = stripeDataDiv ? stripeDataDiv.getAttribute("data-client-secret") : null;

    if (!stripePublicKey) {
        console.error("🚨 ERROR: Stripe public key is missing! Check Django template.");
        alert("Payment setup failed. Please try again or contact support.");
        return;
    }

    if (!clientSecret) {
        console.error("🚨 ERROR: Client Secret is missing! Check Django template.");
        alert("Payment setup failed. Please try again or contact support.");
        return;
    }

    try {
        // ✅ Initialize Stripe
        const stripe = Stripe(stripePublicKey);
        const elements = stripe.elements({ clientSecret: clientSecret });

        console.log("🎯 Stripe initialized successfully");

        // ✅ Create and mount the payment element
        const paymentElement = elements.create('payment');
        paymentElement.mount('#payment-element');
        console.log("✅ Stripe Elements Mounted");

        // ✅ Handle form submission
        handlePaymentForm(stripe, elements, clientSecret, orderNumber);

    } catch (error) {
        console.error("🚨 Stripe Initialization Error:", error);
        alert("Error initializing payment. Please refresh and try again.");
    }
});

/**
 * ✅ Handles form submission and Stripe payment confirmation
 */
function handlePaymentForm(stripe, elements, clientSecret, orderNumber) {
    const form = document.getElementById('payment-form');
    if (!form) {
        console.error("🚨 ERROR: Payment form not found!");
        return;
    }

    const loadingSpinner = document.getElementById('payment-overlay');
    const errorContainer = document.getElementById('card-errors');
    const submitButton = form.querySelector('button[type="submit"]');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        console.log("🛒 Processing payment...");

        submitButton.disabled = true;
        if (loadingSpinner) loadingSpinner.classList.remove("d-none");
        if (errorContainer) errorContainer.textContent = "";

        try {
            console.log("⚡ Sending request to Stripe for payment confirmation...");
            const { error, paymentIntent } = await stripe.confirmPayment({
                elements,
                confirmParams: {
                    return_url: window.location.origin + `/checkout/checkout-success/${orderNumber}/`,  // ✅ Direct Redirect
                },
            });

            if (error) {
                console.error("🚨 Stripe Payment Error:", error.message);
                errorContainer.textContent = "Payment failed: " + error.message;
            } else if (paymentIntent && paymentIntent.status === 'succeeded') {
                console.log("✅ Payment successful! Redirecting...");
                window.location.href = `/checkout/checkout-success/${orderNumber}/`;  // ✅ Instant Redirect
            }
        } catch (err) {
            console.error("🚨 Unexpected Payment Error:", err);
            errorContainer.textContent = 'An unexpected error occurred. Please try again.';
        } finally {
            submitButton.disabled = false;
            if (loadingSpinner) loadingSpinner.classList.add("d-none");
        }
    });
}
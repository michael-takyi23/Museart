document.addEventListener("DOMContentLoaded", async function () {
    const stripePublicKey = document.getElementById('id_stripe_public_key')?.textContent.trim();
    const clientSecret = document.getElementById('id_client_secret')?.textContent.trim();

    if (!stripePublicKey) {
        console.error("Stripe public key is missing!");
        return;
    }

    if (!clientSecret) {
        console.error("Client secret is missing! Payment Intent may not have been created.");
        const errorContainer = document.getElementById('card-errors');
        if (errorContainer) {
            errorContainer.textContent = "Error: Payment cannot be processed.";
        }
        return;
    }

    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements({
        clientSecret: clientSecret,
        appearance: {
            theme: 'flat',
            variables: {
                colorPrimary: '#007bff',
                colorText: '#32325d',
                fontFamily: 'Arial, sans-serif',
                fontSizeBase: '16px',
                borderRadius: '5px',
            },
        },
    });

    const paymentElement = elements.create('payment');
    paymentElement.mount('#payment-element');

    const form = document.getElementById('payment-form');
    const loadingSpinner = document.getElementById('payment-overlay');
    const errorContainer = document.getElementById('card-errors');
    const submitButton = form.querySelector('button[type="submit"]');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        if (loadingSpinner) loadingSpinner.classList.remove("d-none");
        submitButton.disabled = true;
        if (errorContainer) errorContainer.textContent = "";

        try {
            const { error, paymentIntent } = await stripe.confirmPayment({
                elements,
                confirmParams: {
                    return_url: window.location.href,
                },
            });

            if (error) {
                console.error("Payment error:", error.message);
                if (errorContainer) errorContainer.textContent = error.message;
            } else if (paymentIntent && paymentIntent.status === 'succeeded') {
                console.log("Payment successful!");
                fetch("/checkout/", { method: "POST" })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            window.location.href = data.redirect_url;
                        } else {
                            if (errorContainer) errorContainer.textContent = "Error processing payment. Please contact support.";
                        }
                    })
                    .catch(err => {
                        console.error("Unexpected error:", err);
                        if (errorContainer) errorContainer.textContent = 'An unexpected error occurred.';
                    });
            } else {
                if (errorContainer) errorContainer.textContent = "Payment processing error. Please try again.";
            }
        } catch (err) {
            console.error("Unexpected error:", err);
            if (errorContainer) errorContainer.textContent = 'An unexpected error occurred.';
        } finally {
            submitButton.disabled = false;
            if (loadingSpinner) loadingSpinner.classList.add("d-none");
        }
    });

    const queryClientSecret = new URLSearchParams(window.location.search).get('payment_intent_client_secret');
    if (queryClientSecret) {
        stripe.retrievePaymentIntent(queryClientSecret).then(({ paymentIntent }) => {
            const messageContainer = document.getElementById('message');
            if (paymentIntent && messageContainer) {
                switch (paymentIntent.status) {
                    case 'succeeded':
                        messageContainer.innerText = 'Success! Payment received.';
                        setTimeout(() => window.location.href = window.location.href, 2000);
                        break;
                    case 'processing':
                        messageContainer.innerText = "Payment processing. We'll update you soon.";
                        break;
                    case 'requires_action':
                        messageContainer.innerText = "Additional authentication is required.";
                        break;
                    default:
                        messageContainer.innerText = 'Something went wrong. Please try again.';
                }
            }
        }).catch((err) => {
            console.error("Error retrieving payment intent:", err);
        });
    }
});

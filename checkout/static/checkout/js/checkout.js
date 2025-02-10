// Wait for DOM to load before executing script
document.addEventListener("DOMContentLoaded", async function () {

    // Get Stripe keys and clientSecret from the template
    const stripePublicKey = document.getElementById('id_stripe_public_key')?.textContent.trim();
    const clientSecret = document.getElementById('id_client_secret')?.textContent.trim();
    const successUrl = document.getElementById('id_success_url')?.value;

    // Ensure Stripe public key is available
    if (!stripePublicKey) {
        console.error("Stripe public key is missing!");
        return;
    }

    if (!clientSecret) {
        console.error("Client secret is missing! Payment Intent may not have been created.");
        document.getElementById('card-errors').textContent = "Error: Payment cannot be processed.";
        return;
    }

    // Initialize Stripe
    const stripe = Stripe(stripePublicKey);

    // Stripe Elements options
    const options = {
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
    };

    // Create Stripe elements
    const elements = stripe.elements(options);
    const paymentElement = elements.create('payment');
    paymentElement.mount('#payment-element');

    // Form Submission Handler
    const form = document.getElementById('payment-form');
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorContainer = document.getElementById('card-errors');
    const submitButton = form.querySelector('button[type="submit"]');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Show spinner and disable button
        loadingSpinner.style.display = 'block';
        submitButton.disabled = true;

        try {
            const { error, paymentIntent } = await stripe.confirmPayment({
                elements,
                confirmParams: {
                    return_url: successUrl,  // Redirect after successful payment
                },
            });

            if (error) {
                console.error("Payment error:", error.message);
                errorContainer.textContent = error.message;
            } else if (paymentIntent && paymentIntent.status === 'succeeded') {
                console.log("Payment successful!");
                window.location.href = successUrl; // Redirect on success
            } else {
                errorContainer.textContent = "Payment processing error. Please try again.";
            }
        } catch (err) {
            console.error("Unexpected error:", err);
            errorContainer.textContent = 'An unexpected error occurred.';
        } finally {
            submitButton.disabled = false;
            loadingSpinner.style.display = 'none';
        }
    });

    // Handle redirection on page load (for Stripe's PaymentIntent flow)
    const queryClientSecret = new URLSearchParams(window.location.search).get('payment_intent_client_secret');
    if (queryClientSecret) {
        stripe.retrievePaymentIntent(queryClientSecret).then(({ paymentIntent }) => {
            const messageContainer = document.getElementById('message');
            if (paymentIntent) {
                switch (paymentIntent.status) {
                    case 'succeeded':
                        messageContainer.innerText = 'Success! Payment received.';
                        window.location.href = successUrl;
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
        });
    }
});

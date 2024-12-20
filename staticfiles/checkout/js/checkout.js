// Initialize Stripe
const stripePublicKey = document.getElementById('id_stripe_public_key').textContent;
const stripe = Stripe(stripePublicKey);
const clientSecret = document.getElementById('id_client_secret').textContent;
const successUrl = document.getElementById('id_success_url').value;

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
        const { error } = await stripe.confirmPayment({
            elements,
            confirmParams: {
                return_url: successUrl,
            },
        });

        if (error) {
            errorContainer.textContent = error.message;
        }
    } catch (err) {
        errorContainer.textContent = 'An unexpected error occurred.';
    } finally {
        submitButton.disabled = false;
        loadingSpinner.style.display = 'none';
    }
});

// Handle redirection on page load
const queryClientSecret = new URLSearchParams(window.location.search).get('payment_intent_client_secret');
if (queryClientSecret) {
    stripe.retrievePaymentIntent(queryClientSecret).then(({ paymentIntent }) => {
        const messageContainer = document.getElementById('message');
        switch (paymentIntent.status) {
            case 'succeeded':
                messageContainer.innerText = 'Success! Payment received.';
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
    });
}

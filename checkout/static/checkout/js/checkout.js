// Initialize Stripe
const stripePublicKey = document.getElementById('id_stripe_public_key').textContent;
const stripe = Stripe(stripePublicKey);

const clientSecret = document.getElementById('id_client_secret').textContent;

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
// Create and mount Payment Element
const paymentElement = elements.create('payment');
paymentElement.mount('#payment-element');


// Form Submission Handler
const form = document.getElementById('payment-form');
const loadingSpinner = document.getElementById('loading-spinner');
const errorContainer = document.getElementById('card-errors');

form.addEventListener('submit', async (event) => {
    event.preventDefault();

    // Show spinner
    loadingSpinner.style.display = 'block';

    const { error } = await stripe.confirmPayment({
        elements,
        confirmParams: {
            return_url: "{{ success_url }}", // Replace with the success URL passed dynamically
        },
    });

    if (error) {
        // Display error message
        errorContainer.textContent = error.message;
        loadingSpinner.style.display = 'none';
    }
});

// Optional: Handle redirection on page load
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
            default:
                messageContainer.innerText = 'Something went wrong. Please try again.';
        }
    });
}

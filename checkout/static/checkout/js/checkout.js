// Initialize Stripe with your publishable key
const stripe = Stripe('{{ stripe_public_key }}');

// Set up Stripe Elements to use in checkout form, passing the client secret obtained in a previous step
const options = {
    clientSecret: '{{ CLIENT_SECRET }}',  // Replace with the actual client secret from your server
    appearance: {/* Customize appearance if needed */}
};

// Initialize Elements
const elements = stripe.elements(options);

// Create and mount the Payment Element (this is where card details will be entered)
const paymentElement = elements.create('payment');
paymentElement.mount('#payment-element');

// Handle form submission
const form = document.getElementById('payment-form');
form.addEventListener('submit', async (event) => {
    event.preventDefault();

    // Confirm the payment with Stripe
    const {error} = await stripe.confirmPayment({
        elements,
        confirmParams: {
            return_url: '{{ return_url }}',  // Define where the user should be redirected after payment
        },
    });

    if (error) {
        // Display error message to user
        const messageContainer = document.querySelector('#error-message');
        messageContainer.textContent = error.message;
    }
});

// Optional: If handling a redirection after a successful payment, use this to retrieve and show payment intent status
const clientSecret = new URLSearchParams(window.location.search).get('payment_intent_client_secret');

if (clientSecret) {
    stripe.retrievePaymentIntent(clientSecret).then(({paymentIntent}) => {
        const message = document.querySelector('#message');
        switch (paymentIntent.status) {
            case 'succeeded':
                message.innerText = 'Success! Payment received.';
                break;
            case 'processing':
                message.innerText = "Payment processing. We'll update you when payment is received.";
                break;
            case 'requires_payment_method':
                message.innerText = 'Payment failed. Please try another payment method.';
                break;
            default:
                message.innerText = 'Something went wrong.';
                break;
        }
    });
}

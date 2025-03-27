document.addEventListener("DOMContentLoaded", function () {
    console.log("🔄 Initializing Stripe Checkout...");

    const stripePublicKeyEl = document.getElementById("stripe_public_key");
    const clientSecretEl = document.getElementById("client_secret");

    if (!stripePublicKeyEl || !clientSecretEl) {
        console.error("❌ Stripe keys not found. Check template.");
        return;
    }

    const stripePublicKey = JSON.parse(stripePublicKeyEl.textContent);
    const clientSecret = JSON.parse(clientSecretEl.textContent);

    if (!stripePublicKey || !clientSecret) {
        console.error("❌ Invalid Stripe config.");
        return;
    }

    let stripe, elements;
    try {
        stripe = Stripe(stripePublicKey);
        elements = stripe.elements({ clientSecret });
    } catch (err) {
        console.error("❌ Stripe init failed:", err);
        return;
    }

    const paymentElement = elements.create("payment");
    const mountElement = document.getElementById("payment-element");

    if (!mountElement) {
        console.error("❌ Missing #payment-element");
        return;
    }

    try {
        paymentElement.mount("#payment-element");
        console.log("✅ Stripe Payment Element mounted");
    } catch (err) {
        console.error("❌ Mount failed:", err);
    }

    // 🌀 Show loading spinner and cache metadata on submit
    document.getElementById("payment-form")?.addEventListener("submit", async (e) => {
        const overlay = document.getElementById("payment-overlay");
        overlay?.classList.remove("d-none");

        try {
            await cacheCheckoutData(clientSecret);
        } catch (err) {
            console.warn("⚠️ Failed to cache checkout data before submit:", err);
        }
    });
});

// ✅ Cache checkout data before confirming payment
async function cacheCheckoutData(clientSecret) {
    const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;
    const pid = clientSecret.split('_secret')[0];
    if (!pid) throw new Error("Invalid client secret");

    const response = await fetch("/checkout/cache-checkout-data/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": csrfToken
        },
        body: new URLSearchParams({
            csrfmiddlewaretoken: csrfToken,
            client_secret: clientSecret,
            save_info: document.getElementById('id-save-info')?.checked ? "true" : "false"
        })
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    console.log("✅ Checkout data cached");
}

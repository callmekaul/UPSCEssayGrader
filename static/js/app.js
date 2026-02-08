/* ---------------------------------------------------------------
   Polling logic for the loading page
   --------------------------------------------------------------- */
function startPolling(taskId) {
    const adMinSeconds = 15;
    const countdownEl = document.getElementById("countdown");
    const adPhase = document.getElementById("ad-phase");
    const waitingPhase = document.getElementById("waiting-phase");
    const errorPhase = document.getElementById("error-phase");

    let adTimerDone = false;
    let resultReady = false;
    let redirectUrl = null;

    // Countdown
    let remaining = adMinSeconds;
    const countdownInterval = setInterval(() => {
        remaining--;
        if (countdownEl) countdownEl.textContent = remaining;
        if (remaining <= 0) {
            clearInterval(countdownInterval);
            adTimerDone = true;
            maybeRedirect();
        }
    }, 1000);

    // Poll every 2 seconds
    const pollInterval = setInterval(async () => {
        try {
            const resp = await fetch(`/api/status/${taskId}`);
            const data = await resp.json();

            if (data.status === "done") {
                resultReady = true;
                redirectUrl = data.redirect;
                clearInterval(pollInterval);
                maybeRedirect();
            } else if (data.status === "error") {
                clearInterval(pollInterval);
                clearInterval(countdownInterval);
                document.getElementById("error-msg").textContent =
                    data.error || "An unexpected error occurred.";
                adPhase.classList.add("hidden");
                waitingPhase.classList.add("hidden");
                errorPhase.classList.remove("hidden");
            }
        } catch (e) {
            // Network error — keep trying
        }
    }, 2000);

    function maybeRedirect() {
        if (adTimerDone && resultReady) {
            window.location.href = redirectUrl;
        } else if (adTimerDone && !resultReady) {
            adPhase.classList.add("hidden");
            waitingPhase.classList.remove("hidden");
        }
    }
}

/* ---------------------------------------------------------------
   Donation modal
   --------------------------------------------------------------- */
function openDonationModal() {
    document.getElementById("donation-modal").classList.remove("hidden");
    selectAmount(50);
}

function closeDonationModal() {
    document.getElementById("donation-modal").classList.add("hidden");
}

async function selectAmount(amount) {
    document.querySelectorAll(".amount-btn").forEach((btn) => {
        btn.classList.toggle("active", parseInt(btn.dataset.amount) === amount);
    });

    try {
        const resp = await fetch(`/api/qr/${amount}`);
        const data = await resp.json();

        document.getElementById("qr-image").src = data.qr_data_url;
        document.getElementById("upi-link").href = data.upi_url;

        const caption = document.getElementById("qr-caption");
        caption.textContent =
            amount === 0
                ? "Enter any amount in your UPI app after scanning"
                : "Scan with any UPI app";
    } catch (e) {
        // Silently fail — QR just won't update
    }
}

// Attach click handlers once DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".amount-btn").forEach((btn) => {
        btn.addEventListener("click", () =>
            selectAmount(parseInt(btn.dataset.amount))
        );
    });
});

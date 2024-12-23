function openShareModal(buttonElement) {
    const modal = document.getElementById("shareModal");
    const companyName = buttonElement.getAttribute("data-company");
    modal.setAttribute("data-company", companyName);
    modal.style.display = "flex";
}

function closeShareModal() {
    const modal = document.getElementById("shareModal");
    modal.style.display = "none";
}

function getDealUrl() {
    const modal = document.getElementById("shareModal");
    const company = modal.getAttribute("data-company") || "default";
    const baseUrl = window.location.origin;
    return `${baseUrl}/?company=${encodeURIComponent(company)}`;
}

// Detect if the code is running in a mobile app (basic check)
function isMobileApp() {
    return /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
}

function shareOnFacebook() {
    const url = getDealUrl();
    const shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;

    if (isMobileApp()) {
        // Redirect in the same window for mobile apps
        window.location.href = shareUrl;
    } else {
        // Open in a new window for browsers
        const facebookWindow = window.open(shareUrl, "Share on Facebook", "width=600,height=400,scrollbars=yes");
        if (!facebookWindow) {
            alert("Please enable pop-ups for sharing on Facebook.");
        }
    }
}

function shareOnTwitter() {
    const url = getDealUrl();
    const text = "Check out this amazing deal!";
    const twitterUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`;

    if (isMobileApp()) {
        window.location.href = twitterUrl;
    } else {
        window.open(twitterUrl, "Share on Twitter", "width=600,height=400,scrollbars=yes");
    }
}

function shareOnLinkedIn() {
    const url = getDealUrl();
    const linkedinUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`;

    if (isMobileApp()) {
        window.location.href = linkedinUrl;
    } else {
        window.open(linkedinUrl, "Share on LinkedIn", "width=600,height=400,scrollbars=yes");
    }
}

function shareViaEmail() {
    const url = getDealUrl();
    const subject = "Check out this deal!";
    const emailUrl = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(url)}`;

    window.location.href = emailUrl; // Works universally
}

function shareOnWhatsApp() {
    const url = getDealUrl();
    const message = `Check out this amazing deal: ${url}`;
    const whatsappUrl = `whatsapp://send?text=${encodeURIComponent(message)}`;
    const webUrl = `https://wa.me/?text=${encodeURIComponent(message)}`;

    if (isMobileApp()) {
        // Try WhatsApp app first
        window.location.href = whatsappUrl;

        // Fallback to web WhatsApp after a slight delay
        setTimeout(() => {
            window.location.href = webUrl;
        }, 1500);
    } else {
        // Desktop browsers or non-mobile environments
        window.location.href = webUrl;
    }
}

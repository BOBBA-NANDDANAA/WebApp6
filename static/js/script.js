function openShareModal() {
    const modal = document.getElementById("shareModal");
    modal.style.display = "flex";
}

function closeShareModal() {
    const modal = document.getElementById("shareModal");
    modal.style.display = "none";
}

function getDealUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    const company = urlParams.get('company') || 'default'; // Use 'default' if no company is provided.

    // Get the current domain (works for both local and production)
    const baseUrl = window.location.origin;

    // Always append the 'company' parameter to the base URL
    return `${baseUrl}/?company=${encodeURIComponent(company)}`;
}

function shareOnFacebook() {
    const url = getDealUrl();
    const shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
    window.open(shareUrl, "Share on Facebook", "width=600,height=400,scrollbars=yes");
}

function shareOnTwitter() {
    const url = getDealUrl();
    const text = "Check out this amazing deal!";
    const twitterUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`;
    window.open(twitterUrl, "Share on Twitter", "width=600,height=400,scrollbars=yes");
}

function shareOnLinkedIn() {
    const url = getDealUrl();
    const linkedinUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`;
    window.open(linkedinUrl, "Share on LinkedIn", "width=600,height=400,scrollbars=yes");
}

function shareViaEmail() {
    const url = getDealUrl();
    const subject = "Check out this deal!";
    const emailUrl = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(url)}`;
    window.location.href = emailUrl;
}

function shareOnWhatsApp() {
    const url = getDealUrl();
    const message = `Check out this amazing deal: ${url}`;

    // WhatsApp deep linking for mobile
    const whatsappUrl = `whatsapp://send?text=${encodeURIComponent(message)}`;

    // Fallback URL for when WhatsApp is not installed (opens WhatsApp Web)
    const webUrl = `https://wa.me/?text=${encodeURIComponent(message)}`;

    // Try to open WhatsApp directly (mobile deep linking)
    const openUrl = () => window.location.href = whatsappUrl;

    // If WhatsApp is not available, fallback to WhatsApp Web after a delay
    const timeout = setTimeout(() => {
        window.location.href = webUrl;  // Open WhatsApp Web if the app is not installed
    }, 1000);  // 1 second delay before fallback

    openUrl();  // Attempt to open WhatsApp directly
}

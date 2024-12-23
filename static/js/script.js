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
    const whatsappUrl = `whatsapp://send?text=${encodeURIComponent(message)}`;
    const webUrl = `https://wa.me/?text=${encodeURIComponent(message)}`;

    const openUrl = () => window.location.href = whatsappUrl;
    const timeout = setTimeout(() => {
        window.location.href = webUrl;
    }, 1000);

    openUrl();
}

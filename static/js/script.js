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
    const company = urlParams.get('company');
    
    // If there's a 'company' parameter, append it to the base URL
    if (company) {
        return `http://127.0.0.1:5000/?company=${encodeURIComponent(company)}`;
    }
    
    // Default to the homepage if no company is specified
    return "http://127.0.0.1:5000/";
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
    const url = window.location.href;
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
    const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(message)}`;
    window.open(whatsappUrl, "Share on WhatsApp", "width=600,height=400,scrollbars=yes");
}

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

// Toggle Menu Visibility
function toggleMenu() {
    const menu = document.getElementById('menu');
    menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
}

// Toggle Filters Visibility
function toggleFilters() {
    const filters = document.getElementById('filters');
    filters.style.display = filters.style.display === 'block' ? 'none' : 'block';
}

// Apply Filters (collect selected banks)
function applyFilters() {
    const selectedBanks = Array.from(document.querySelectorAll('input[name="banks"]:checked'))
        .map(checkbox => checkbox.value);

    // TODO: Use `selectedBanks` to filter the deals
    console.log('applyFilters executed');
    console.log('Selected Banks:', selectedBanks);
    fetchFilteredDeals(selectedBanks);
}

// Fetch Filtered Deals from Server
function fetchFilteredDeals(selectedBanks) {
    // Make an AJAX call to fetch filtered deals from the server
    console.log('Fetching deals for:', selectedBanks);

    // Example: Fetch deals (replace `/filter-deals` with your endpoint)
    fetch('/filter-deals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ banks: selectedBanks })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Filtered Deals Received:', data);
            // Update the deals list dynamically (e.g., by manipulating the DOM)
            // Example: updateDealsList(data);
            updateDealsUI(data);
        })
        .catch(err => console.error('Error fetching deals:',err));
}

function updateDealsUI(deals) {
    try {
        const dealsContainer = document.querySelector('.deals');
        dealsContainer.innerHTML = ''; // Clear the existing deals

        if (deals.length === 0) {
            dealsContainer.innerHTML = '<p>No deals found for selected filters.</p>';
            return;
        }

        deals.forEach(deal => {
            const dealCard = document.createElement('div');
            dealCard.classList.add('card');
            dealCard.innerHTML = `
                <img src="${deal.Logo}" alt="${deal.Company} Logo">
                <div class="card-content">
                    <a href="${deal.Bank_Website}" target="_blank">${deal.Bank}</a>
                    <a href="https://www.${deal.CleanName}.com" target="_blank">${deal.Company}</a>
                    <p><strong>Offer:</strong> ${deal.Offer}</p>
                    <p><strong>Expires On:</strong> ${deal['Expire Date']}</p>
                </div>
                <div class="share-box">
                    <button class="share-button" data-company="${deal.Company}" onclick="openShareModal(this)">Share</button>
                </div>
            `;
            dealsContainer.appendChild(dealCard);
        });
    } catch (error) {
        console.error('Error updating deals UI:', error);
    }
}

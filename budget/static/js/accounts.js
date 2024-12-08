document.addEventListener('DOMContentLoaded', function() {
    const walletsContainer = document.getElementById('walletsContainer');
    const walletDetailsModal = new bootstrap.Modal(document.getElementById('walletDetailsModal'));
    const secretKeyForm = document.getElementById('secretKeyForm');
    const balanceDisplay = document.getElementById('balanceDisplay');
    const balanceAmount = document.getElementById('balanceAmount');
    const walletTypeHeader = document.getElementById('walletTypeHeader');
    const walletUsername = document.getElementById('walletUsername');
    const walletDetails = document.getElementById('walletDetails');

    // Mock wallet data (in a real app, this would come from a backend)
    const wallets = [
        {
            id: 1,
            type: 'Mobile Money',
            username: 'john_mobile',
            details: 'Registered Phone: +254712345678',
            secretKey: 'mobile123',
            balance: 5000.50
        },
        {
            id: 2,
            type: 'Bank Account',
            username: 'jane_bank',
            details: 'Account Number: 1234567890',
            secretKey: 'bank456',
            balance: 25000.75
        },
        {
            id: 3,
            type: 'Crypto Wallet',
            username: 'crypto_trader',
            details: 'Wallet Address: 0x1234...5678',
            secretKey: 'crypto789',
            balance: 0.5
        }
    ];

    // Render wallet cards
    function renderWallets() {
        walletsContainer.innerHTML = '';
        wallets.forEach(wallet => {
            const walletCard = document.createElement('div');
            walletCard.className = 'col-md-4 mb-3';
            walletCard.innerHTML = `
                <div class="card wallet-card" data-wallet-id="${wallet.id}">
                    <div class="card-body">
                        <h5 class="card-title">${wallet.type}</h5>
                        <p class="card-text">Username: ${wallet.username}</p>
                    </div>
                </div>
            `;
            walletCard.addEventListener('click', () => showWalletDetails(wallet));
            walletsContainer.appendChild(walletCard);
        });
    }

    // Show wallet details in modal
    function showWalletDetails(wallet) {
        // Reset previous state
        secretKeyForm.reset();
        balanceDisplay.style.display = 'none';
        
        // Set wallet information
        walletTypeHeader.textContent = wallet.type;
        walletUsername.textContent = wallet.username;
        walletDetails.textContent = wallet.details;

        // Store current wallet for secret key verification
        window.currentWallet = wallet;

        // Show modal
        walletDetailsModal.show();
    }

    // Secret key form submission
    secretKeyForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const secretKeyInput = document.getElementById('secretKeyInput');
        
        // Verify secret key
        if (secretKeyInput.value === window.currentWallet.secretKey) {
            // Show balance
            balanceAmount.textContent = window.currentWallet.balance.toLocaleString('en-US', {
                style: 'currency',
                currency: 'USD'
            });
            balanceDisplay.style.display = 'block';
        } else {
            alert('Incorrect secret key. Access denied.');
            secretKeyInput.value = '';
        }
    });

    // Initial render
    renderWallets();
});
/**
 * CrisisSignal AI — Voting Module
 * Handles crowd verification votes with optimistic UI updates.
 */

/**
 * Cast a vote on an alert (confirm or reject).
 * @param {number} alertId - The alert ID
 * @param {string} voteType - 'confirm' or 'reject'
 */
async function castVote(alertId, voteType) {
    // Disable buttons immediately (optimistic)
    const container = document.getElementById(`vote-actions-${alertId}`);
    if (container) {
        const buttons = container.querySelectorAll('button');
        buttons.forEach(btn => {
            btn.disabled = true;
            btn.style.opacity = '0.5';
        });

        // Show loading state on clicked button
        const clickedBtn = voteType === 'confirm'
            ? (document.getElementById(`vote-confirm-${alertId}`) || document.getElementById(`btn-confirm-${alertId}`))
            : (document.getElementById(`vote-reject-${alertId}`) || document.getElementById(`btn-reject-${alertId}`));

        if (clickedBtn) {
            clickedBtn.innerHTML = `<span class="spinner spinner-sm"></span> Voting...`;
        }
    }

    try {
        const response = await fetch(`/api/alerts/${alertId}/vote`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ vote: voteType }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Vote failed');
        }

        // Replace vote buttons with "voted" badge
        if (container) {
            container.innerHTML = `
                <div class="voted-badge">
                    <i data-lucide="${voteType === 'confirm' ? 'check' : 'x'}"></i>
                    <span>You voted: ${voteType.toUpperCase()}</span>
                </div>
            `;
            lucide.createIcons();
        }

        // Update confidence display if on detail page
        const confBar = document.querySelector(`#confidence-bar-${alertId} .confidence-fill`);
        if (confBar) {
            confBar.style.width = `${Math.round(data.alert.confidence * 100)}%`;
        }

        const confValue = document.getElementById(`confidence-value-${alertId}`);
        if (confValue) {
            confValue.textContent = `${Math.round(data.alert.confidence * 100)}%`;
        }

        // Update vote counts
        const confirmCount = document.getElementById(`confirm-count-${alertId}`);
        const rejectCount = document.getElementById(`reject-count-${alertId}`);
        if (confirmCount) confirmCount.textContent = data.alert.confirmations_count;
        if (rejectCount) rejectCount.textContent = data.alert.rejections_count;

        // Status change notification
        if (data.status_changed) {
            if (typeof showToast !== 'undefined') {
                showToast(
                    `Alert status changed: ${data.old_status} → ${data.new_status.toUpperCase()}`,
                    data.new_status === 'critical' ? 'error' : 'warning'
                );
            }
        }

        // Success feedback
        if (typeof showToast !== 'undefined') {
            showToast(`Vote recorded: ${voteType.toUpperCase()}`, 'success');
        }

    } catch (error) {
        console.error('[Vote] Error:', error);

        // Re-enable buttons on error
        if (container) {
            const buttons = container.querySelectorAll('button');
            buttons.forEach(btn => {
                btn.disabled = false;
                btn.style.opacity = '1';
            });

            // Restore button text
            const confirmBtn = document.getElementById(`vote-confirm-${alertId}`) || document.getElementById(`btn-confirm-${alertId}`);
            const rejectBtn = document.getElementById(`vote-reject-${alertId}`) || document.getElementById(`btn-reject-${alertId}`);
            if (confirmBtn) confirmBtn.innerHTML = '<i data-lucide="check"></i> Confirm';
            if (rejectBtn) rejectBtn.innerHTML = '<i data-lucide="x"></i> Reject';
            lucide.createIcons();
        }

        if (typeof showToast !== 'undefined') {
            showToast(error.message, 'error');
        } else {
            alert(error.message);
        }
    }
}

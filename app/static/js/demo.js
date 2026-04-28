/**
 * CrisisSignal AI — Demo Mode Runner (demo.js)
 * Runs scripted scenarios with auto-voting.
 */

let demoScenarios = {};
let demoRunning = false;

/**
 * Run a demo scenario: create alert then auto-vote
 */
async function runScenario(scenarioKey) {
    if (demoRunning) {
        showToast('A scenario is already running. Please wait.', 'warning');
        return;
    }

    demoRunning = true;
    const logContainer = document.getElementById('demo-log');
    const logEntries = document.getElementById('log-entries');
    logContainer.style.display = 'block';
    logEntries.innerHTML = '';

    try {
        // Fetch scenarios
        const scenarios = await API.getDemoScenarios();
        const scenario = scenarios[scenarioKey];

        if (!scenario) {
            showToast('Scenario not found', 'error');
            demoRunning = false;
            return;
        }

        addLog(logEntries, `🎬 Starting scenario: ${scenario.name}`);
        addLog(logEntries, `📝 Submitting report: "${scenario.message.substring(0, 60)}..."`);

        // Step 1: Create alert
        const alert = await API.createAlert(scenario.message, scenario.location);
        addLog(logEntries, `✅ Alert created: #${alert.id} | Type: ${alert.type.toUpperCase()} | Severity: ${alert.severity}/10 | Confidence: ${Math.round(alert.confidence * 100)}%`);

        // Step 2: Auto-vote with delays
        for (const vote of scenario.simulated_votes) {
            addLog(logEntries, `⏳ Waiting for ${vote.user}...`);

            await sleep(vote.delay);

            try {
                const result = await API.castVote(alert.id, vote.vote);
                const emoji = vote.vote === 'confirm' ? '✅' : '❌';
                addLog(logEntries, `${emoji} ${vote.user} voted ${vote.vote.toUpperCase()} → Confidence: ${Math.round(result.alert.confidence * 100)}% | Status: ${result.alert.status.toUpperCase()}`);

                if (result.status_changed) {
                    addLog(logEntries, `🔄 STATUS CHANGE: ${result.old_status.toUpperCase()} → ${result.new_status.toUpperCase()}`);
                }
            } catch (err) {
                addLog(logEntries, `⚠️ Vote skipped (${err.message})`);
            }
        }

        addLog(logEntries, `🏁 Scenario complete!`);
        showToast(`Demo "${scenario.name}" completed!`, 'success');

    } catch (error) {
        addLog(logEntries, `❌ Error: ${error.message}`);
        showToast('Demo failed: ' + error.message, 'error');
    }

    demoRunning = false;
}

async function resetSystem() {
    if (!confirm('Reset all alerts? This cannot be undone.')) return;

    try {
        await API.resetSystem();
        showToast('System reset successfully!', 'success');
        const logEntries = document.getElementById('log-entries');
        if (logEntries) logEntries.innerHTML = '';
    } catch (error) {
        showToast('Reset failed: ' + error.message, 'error');
    }
}

function addLog(container, message) {
    const entry = document.createElement('div');
    entry.style.padding = '4px 0';
    entry.style.borderBottom = '1px solid var(--border-subtle)';
    const time = new Date().toLocaleTimeString();
    entry.innerHTML = `<span style="color: var(--text-muted);">[${time}]</span> ${message}`;
    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

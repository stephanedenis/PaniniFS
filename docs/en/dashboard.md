---
title: Dashboard
---

# 🏕️ Dashboard

This dashboard shows the system state and active components.

## System status

<div id="system-status-loading">
    <p>⏳ Loading system state...</p>
</div>

<div id="system-status" style="display: none;">
    <!-- Dynamic content injected by JavaScript -->
</div>

## 🤖 Autonomous agents

<div id="agents-status">
    <!-- Agents loaded dynamically -->
</div>

## 🌐 Domains

<div id="domains-status">
    <!-- Domains loaded dynamically -->
</div>

## 🔧 GitHub Workflows

<div id="workflows-status">
    <!-- Workflows loaded dynamically -->
</div>

<script>
async function loadStatus() {
    try {
        const response = await fetch('/data/system_status.json');
        const data = await response.json();

        document.getElementById('system-status-loading').style.display = 'none';
        document.getElementById('system-status').style.display = 'block';

        const statusDiv = document.getElementById('system-status');
        statusDiv.innerHTML = `
            <ul>
                <li><strong>Overall status:</strong> ${data.system_health?.overall_status || 'Unknown'}</li>
                <li><strong>Last check:</strong> ${data.system_health?.last_health_check || data.timestamp || 'N/A'}</li>
            </ul>
        `;

        if (data.agents) {
            const agentsDiv = document.getElementById('agents-status');
            const agentList = (data.agents.agents || []).map(a =>
                `<li>${a.name} — <em>${a.status}</em></li>`
            ).join('');
            agentsDiv.innerHTML = `<ul>${agentList}</ul>`;
        }

        if (data.domains?.configured) {
            const domainsDiv = document.getElementById('domains-status');
            const domainList = data.domains.configured.map(d =>
                `<li><strong>${d.domain}</strong> — ${d.status} (SSL: ${d.ssl})</li>`
            ).join('');
            domainsDiv.innerHTML = `<ul>${domainList}</ul>`;
        }
    } catch (e) {
        document.getElementById('system-status-loading').innerHTML = '<p>⚠️ Could not load status data.</p>';
    }
}
loadStatus();
</script>

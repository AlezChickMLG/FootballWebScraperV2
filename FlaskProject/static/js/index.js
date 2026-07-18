import { sanitizeSearchName } from "./utils.js";

async function searchMatches(button_id, fetch_url) {
    const input = document.getElementById(button_id);
    if (!input) {
        console.error(`Input ${button_id} inexistent`);
        return;
    }

    const team_name = sanitizeSearchName(input.value);
    if (!team_name) {
        showListMessage("Introdu numele unei echipe.");
        return;
    }

    showListMessage(`Se caută meciurile echipei... ${team_name}`);

    try {
        const response = await fetch(`${fetch_url}/${encodeURIComponent(team_name)}`);

        // incearca sa citesti JSON-ul indiferent de status (backend-ul trimite
        // mesaj_eroare si pe 404/500)
        let data;
        try {
            data = await response.json();
        } catch {
            data = null;
        }

        if (!response.ok) {
            const msg = data?.mesaj_eroare || "Eroare la procesarea meciurilor.";
            showListMessage(msg);
            return;
        }

        if (!Array.isArray(data)) {
            console.error("Răspuns neașteptat (nu e array):", data);
            showListMessage("Răspuns invalid de la server.");
            return;
        }

        if (data.length === 0) {
            showListMessage("Niciun meci găsit pentru această echipă.");
            return;
        }

        renderMatches(data);
    } catch (error) {
        console.error("Eroare de rețea:", error);
        showListMessage("Nu s-a putut contacta serverul.");
    }
}

function showListMessage(message) {
    const list = document.getElementById("list");
    if (list) {
        list.innerHTML = `<p class="list-message">${message}</p>`;
    }
}

function renderMatches(matches) {
    const list = document.getElementById("list");
    if (!list) return;

    list.innerHTML = matches.map(match => `
        <div class="card">
            <div class="team-block home">
                <img src="${match.home_flag || ''}" class="flag" alt="${match.home_team || 'Home'}"
                     onerror="this.style.visibility='hidden'">
                <span class="team_name">${match.home_team || '?'}</span>
                <div class="home-team-container" id="team-${match.home_team_id}"></div>
            </div>
            <div class="vs">
                ${match.match_score
                    ? `<div class="score">${match.match_score}</div>`
                    : `<div class="vs-label">vs</div>`}
                <div class="start_time">${match.start_time || ''}</div>
            </div>
            <div class="team-block away">
                <img src="${match.away_flag || ''}" class="flag" alt="${match.away_team || 'Away'}"
                     onerror="this.style.visibility='hidden'">
                <span class="team_name">${match.away_team || '?'}</span>
                <div class="away-team-container" id="team-${match.away_team_id}"></div>
            </div>
            <div class="statistics-button">
                <button onclick="getStatistics('${match.mid}', this)">Obține statisticile</button>
            </div>
            <div class="statistics-container" id="stats-${match.mid}"></div>
        </div>
    `).join("");
}

async function getStatistics(mid, button) {
    const container = document.getElementById(`stats-${mid}`);
    if (!container) return;

    // toggle: daca sunt deja afisate, le ascundem
    if (container.classList.contains("open")) {
        container.classList.remove("open");
        container.innerHTML = "";
        button.textContent = "Obține statisticile";
        return;
    }

    button.textContent = "Se încarcă...";
    button.disabled = true;

    try {
        const response = await fetch(`/get_statistics/${mid}`);

        let statistics;
        try {
            statistics = await response.json();
        } catch {
            statistics = null;
        }

        if (!response.ok) {
            const msg = statistics?.mesaj_eroare || "Nu s-au putut încărca statisticile.";
            container.innerHTML = `<p class="stats-error">${msg}</p>`;
            container.classList.add("open");
            button.textContent = "Obține statisticile";
            return;
        }

        container.innerHTML = renderStatistics(statistics);
        container.classList.add("open");
        button.textContent = "Ascunde statisticile";
    } catch (error) {
        console.error("Eroare la statistici:", error);
        container.innerHTML = `<p class="stats-error">Nu s-au putut încărca statisticile.</p>`;
        container.classList.add("open");
        button.textContent = "Obține statisticile";
    } finally {
        button.disabled = false;
    }
}

function renderStatistics(statistics) {
    if (!statistics || Object.keys(statistics).length === 0) {
        return `<p class="stats-error">Nu există statistici pentru acest meci.</p>`;
    }

    return Object.entries(statistics).map(([category, stats]) => `
        <div class="stat-category">
            <div class="stat-category-title">${category}</div>
            ${Object.entries(stats).map(([name, values]) => `
                <div class="stat-row">
                    <span class="stat-home">${values?.home ?? '-'}</span>
                    <span class="stat-name">${name}</span>
                    <span class="stat-away">${values?.away ?? '-'}</span>
                </div>
            `).join("")}
        </div>
    `).join("");
}

async function getMatches() {
    await searchMatches('find_button', 'get_matches');
}

async function scanMatches() {
    await searchMatches('find_button', 'scan_matches');
}

window.getMatches = getMatches;
window.scanMatches = scanMatches;
window.getStatistics = getStatistics;


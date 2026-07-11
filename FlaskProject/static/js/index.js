async function searchMatches() {
    let team_name = document.getElementById("find_button").value;
    console.log("Cautam meciurile echipei " + team_name);

    let response = await fetch("get_matches/" + team_name);

    if (response.status === 200) {
        let matches = await response.json();
        console.log(matches);

        if (Array.isArray(matches)) {
            renderMatches(matches);
            console.log("Meciuri randate");
        }

        else {
            console.log("Nu este Array");
        }
    }

    else {
        console.log("Eroare la procesarea meciurilor");
    }
}

function renderMatches(matches) {
    let list = document.getElementById("list");

    list.innerHTML = matches.map(match => `
        <div class="card">
            <div class="team-block home">
                <img src="${match.home_flag}" class="flag" alt="Home team">
                <span class="team_name">${match.home_team}</span>
            </div>
            <div class="vs">vs
                <div class="start_time">${match.start_time}</div>
            </div>
            <div class="team-block away">
                <img src="${match.away_flag}" class="flag" alt="Away team">
                <span class="team_name">${match.away_team}</span>
            </div>
        </div>
    `).join("");
}
async function loadCyLab() {

    console.log("Loading CyLab...");

    const response = await fetch("data/stats.json?" + Date.now());

    console.log(response.status);

    const stats = await response.json();

    console.log(stats);

    document.getElementById("cylab-progress").textContent =
        stats.overall.percentage + "%";

    document.getElementById("cylab-solved").textContent =
        `${stats.overall.solved}/${stats.overall.available}`;

    document.getElementById("easy-stat").textContent =
        `${stats.difficulty.easy.solved}/${stats.difficulty.easy.available}`;

    document.getElementById("medium-stat").textContent =
        `${stats.difficulty.medium.solved}/${stats.difficulty.medium.available}`;

    document.getElementById("hard-stat").textContent =
        `${stats.difficulty.hard.solved}/${stats.difficulty.hard.available}`;

    document.getElementById("overall-bar").style.width =
        stats.overall.percentage + "%";

    console.log("Updated.");
}

loadCyLab();
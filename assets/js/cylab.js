async function loadCyLab(){

    const response = await fetch("./data/stats.json");

    const stats = await response.json();

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

}

loadCyLab();
async function loadStats() {
    const res = await fetch("./data/stats.json");
    const stats = await res.json();

    document.getElementById("overallSolved").textContent =
        stats.overall.solved;

    document.getElementById("overallAvailable").textContent =
        stats.overall.available;

    document.getElementById("overallPercent").textContent =
        stats.overall.percentage + "%";

    document.getElementById("progressBar").style.width =
        stats.overall.percentage + "%";
}

loadStats();

function openNav() {
    document.getElementById("mySidebar").classList.add("expanded");
    document.getElementById("main").style.marginLeft = "23%";
}

function closeNav() {
    document.getElementById("mySidebar").classList.remove("expanded");
    document.getElementById("main").style.marginLeft = "6%";
}

function handleSearchInput(event) {
    const query = event.target.value.toLowerCase();
    const resultsContainer = document.getElementById("autocomplete-results");
    resultsContainer.innerHTML = ""; // Clear previous results

    if (query.length < 2) {
        resultsContainer.style.display = "none";
        return;
    }

    const filteredProjects = Object.values(projects).filter(project =>
        project.name.toLowerCase().includes(query)
    );

    if (filteredProjects.length > 0) {
        resultsContainer.style.display = "block";
        filteredProjects.forEach(project => {
            const item = document.createElement("div");
            item.className = "autocomplete-item";
            item.textContent = project.name;
            item.onclick = () => {
                document.getElementById("search-input").value = project.name;
                resultsContainer.style.display = "none";
            };
            resultsContainer.appendChild(item);
        });
    } else {
        resultsContainer.style.display = "none";
    }
}
$(function () {
    $("#sortable").sortable({
        axis: "y", // Allow vertical sorting only
        revert: 200, // Smooth animation when dropping
        placeholder: "sortable-placeholder", // Add a placeholder for better visual feedback
        tolerance: "pointer", // Makes the drop position clearer
        cursor: "move", // Change the cursor to indicate dragging
        opacity: 0.8, // Make the dragged item semi-transparent
        start: function (event, ui) {
            ui.item.addClass("dragging"); // Add a class to the dragged item
        },
        stop: function (event, ui) {
            ui.item.removeClass("dragging"); // Remove the class after dropping
        }
    });

    $("#draggable").draggable({
        connectToSortable: "#sortable",
        helper: "clone",
        revert: "invalid",
        cursor: "move"
    });

    $("ul, li").disableSelection();
});

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
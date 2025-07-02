$(function () {
    $("#sortable").sortable({
        axis: "y", 
        revert: 200, 
        placeholder: "sortable-placeholder", 
        tolerance: "pointer", 
        cursor: "move", 
        opacity: 0.8,
        start: function (event, ui) {
            ui.item.addClass("dragging"); 
        },
        stop: function (event, ui) {
            ui.item.removeClass("dragging"); 
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
}

function closeNav() {
    document.getElementById("mySidebar").classList.remove("expanded");
}

document.addEventListener("DOMContentLoaded", function () {
    handleCurrentProject();
});

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
                // Use handleCurrentProject logic to set active project
                fetch(`/set_active_project`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ project_id: project.id }),
                }).then(response => {
                    if (response.ok) {
                        location.reload();
                    } else {
                        console.error("Failed to set the active project.");
                    }
                });
            };
            resultsContainer.appendChild(item);
        });
    } else {
        resultsContainer.style.display = "none";
    }
}

function handleCurrentProject() {
    const projects = document.querySelectorAll(".project-item, .dropdown-project-item");
    projects.forEach(project => {
        const projectId = project.getAttribute("id");
        project.addEventListener("click", function () {
            fetch(`/set_active_project`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ project_id: projectId }),
            }).then(response => {
                if (response.ok) {
                    location.reload(); 
                } else {
                    console.error("Failed to set the active project.");
                }
            });
        });
    });
}

function tabStyleAdapter() {
    const tasks_tab = document.querySelectorAll("#tasks");
    if( sessionStorage.getItem("user_role") === "user" ) {
        tasks_tab.style.borderRadius = "0px 0px 0px 0px";
    }
}

function toolbarIcons(){
    document.addEventListener("DOMContentLoaded", function () {
        const calendar = document.querySelector(".calendar-icon");
        calendar.addEventListener("click", function () {
            window.location.href = "/calendar"
        });
    });
}
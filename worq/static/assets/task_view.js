document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.getElementById("toggle-view");
    const taskContainer = document.getElementById("task-container");
    const tasks = document.querySelectorAll(".task-item");
    const taskElements = document.querySelectorAll(".task-element");

    toggleButton.addEventListener("click", function () {
        if (taskContainer.classList.contains("card-view")) {
            taskContainer.classList.remove("card-view");
            taskContainer.classList.remove("row");
            taskContainer.classList.add("list-view");
            toggleButton.innerHTML = "view_module";
            tasks.forEach(task => {
                task.classList.remove("col-3");
                task.classList.add("row");
            });
            taskElements.forEach(taskElement => {
                taskElement.classList.add("col-2");
            });
        } else {
            taskContainer.classList.remove("list-view");
            taskContainer.classList.add("card-view");
            taskContainer.classList.add("row");
            tasks.forEach(task => {
                task.classList.add("col-3");
                task.classList.remove("row");
            });
            taskElements.forEach(taskElement => {
                taskElement.classList.remove("col-2");
            });
            toggleButton.innerHTML = "view_list"; 
        }
    });
});
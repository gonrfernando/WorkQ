document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.getElementById("toggle-view");
    const taskContainers = document.querySelectorAll(".task-container");
    const tasks = document.querySelectorAll(".task-spacer");
    const taskElements = document.querySelectorAll(".task-element");
    const taskSubheaders = document.querySelectorAll(".task-subheader");
    const taskPriorities = document.querySelectorAll(".priority");
    const taskDueDates = document.querySelectorAll(".task-due-date");

    const modal = document.getElementById("task-modal");
    const modalContent = document.querySelector(".task-modal-content");
    const closeModal = document.getElementById("close-modal");
    const saveTaskButton = document.getElementById("save-task");
    const deliverTaskButton = document.getElementById("deliver-task");
    const taskTitleModal = document.querySelector(".task-title-modal");
    const taskPriorityModal = document.querySelector(".task-priority-modal .task-priority");
    const taskDueDateModal = document.querySelector(".task-due-date-modal .due-date-text");
    const taskDescriptionModal = document.querySelector(".task-description-modal");
    const requirementsList = document.getElementById("requirements-list");

    toggleButton.addEventListener("click", function () {
        taskContainers.forEach(taskContainer => {
            if (taskContainer.classList.contains("card-view")) {
                // Switch to list view
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

                taskSubheaders.forEach(taskSubheader => {
                    taskSubheader.classList.add("col-4");
                });

                taskPriorities.forEach(priority => {
                    priority.classList.remove("col-4");
                    priority.classList.add("col-3");
                });

                taskDueDates.forEach(dueDate => {
                    dueDate.classList.remove("col-8");
                    dueDate.classList.add("col-6");
                });

            } else {
                // Switch to card view
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

                taskSubheaders.forEach(taskSubheader => {
                    taskSubheader.classList.remove("col-4"); 
                });

                taskPriorities.forEach(priority => {
                    priority.classList.remove("col-3");
                    priority.classList.add("col-4");
                });

                taskDueDates.forEach(dueDate => {
                    dueDate.classList.remove("col-6");
                    dueDate.classList.add("col-8");
                });

                toggleButton.innerHTML = "view_list";
            }
        });
    });

    tasks.forEach(task => {
        task.addEventListener("click", function () {
            const title = task.querySelector(".task-title").textContent;
            const priority = task.querySelector(".task-priority").classList[1];
            const dueDate = task.querySelector(".due-date-text").textContent;
            const description = task.querySelector(".task-description").textContent;
            const requirements = task.querySelectorAll(".custom-checkbox-label");

            taskTitleModal.textContent = title;
            taskPriorityModal.className = `task-priority ${priority}`;
            taskDueDateModal.textContent = dueDate;
            taskDescriptionModal.textContent = description;

            requirementsList.innerHTML = "";
            requirements.forEach(req => {
                const div = document.createElement("div");
                div.style.display = "flex";
                div.style.marginBottom = "2px";
                div.innerHTML = `
                    <label class="checkbox-container">
                        <input class="custom-checkbox" id="requirement-${req.id}" type="checkbox" ${req.checked ? "checked" : ""}>
                        <span class="checkmark"></span>
                        </label>
                    <label for="${req.id}">${req.textContent}</label>
                `;
                requirementsList.appendChild(div);
            });

            modal.style.display = "flex";
        });
    });

    closeModal.addEventListener("click", function () {
        modal.style.display = "none";
    });

    modal.addEventListener("click", function (e) {
        if (e.target === modal) {
            modal.style.display = "none";
        }
    });

    saveTaskButton.addEventListener("click", function () {
        modal.style.display = "none";
    });

    deliverTaskButton.addEventListener("click", function () {
        modal.style.display = "none";
    });
});
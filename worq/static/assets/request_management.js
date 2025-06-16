
function openTaskModalFromCard(element) {
    const taskId = element.getAttribute('data-task-id');
    if (!taskId) {
        console.warn("No task ID found.");
        return;
    }
    if (!Array.isArray(window.tasks)) {
        console.error("window.tasks is not an array", window.tasks);
        return;
    }

    document.getElementById('modal-task-id').value = taskId;
    const selectedTask = window.tasks.find(t => t.id == taskId);
    if (selectedTask) {
        document.querySelector(".task-title-modal").innerText = selectedTask.title;
        document.querySelector(".task-description-modal").innerText = selectedTask.description;
        document.querySelector(".task-priority-modal").innerHTML = `Priority: <span class="task-priority ${selectedTask.priority.toLowerCase()}"></span>`;
        document.querySelector(".task-due-date-modal .due-date-text").innerText = selectedTask.due_date;
        document.querySelector(".project-name-modal").innerText = "Project: " + selectedTask.project_name;
        const requirementsContainer = document.getElementById("requirements-list");
        requirementsContainer.innerHTML = '';
        selectedTask.requirements.forEach(req => {
            const reqDiv = document.createElement("div");
            reqDiv.style.display = "flex";
            reqDiv.innerHTML = `
                <label class="checkbox-container">
                    <input class="custom-checkbox" type="checkbox" ${req.is_completed ? "checked" : ""}>
                    <span class="checkmark"></span>
                </label>
                <label class="custom-checkbox-label">${req.requirement}</label>
            `;
            requirementsContainer.appendChild(reqDiv);
        });
        const container = document.getElementById('task-requests-container');
        container.innerHTML = '';
        selectedTask.requests.forEach(req => {
            let statusClass = '';
            if (req.accepted_by) {
                statusClass = 'request-accepted';
            } else if (req.rejected_by) {
                statusClass = 'request-rejected';
            }
            const requestHtml = `
                <div class="border p-2 mb-2 ${statusClass}">
                    <strong>Action:</strong> ${req.action_type}<br>
                    <strong>Status:</strong> ${req.status}<br>
                    <strong>Reason:</strong> ${req.reason}<br>
                    <strong>Date:</strong> ${req.date}<br>
                    ${!req.accepted_by && !req.rejected_by ? `
                        <button class="btn btn-success btn-sm" onclick="handleRequestAction(${req.id}, 'accept')">Accept</button>
                        <button class="btn btn-danger btn-sm" onclick="handleRequestAction(${req.id}, 'reject')">Reject</button>
                    ` : ''}
                </div>
            `;
            const tempDiv = document.createElement("div");
            tempDiv.innerHTML = requestHtml;
            container.appendChild(tempDiv.firstElementChild);
        });
    } else {
        document.getElementById('task-requests-container').innerHTML = "<p>No requests for this task.</p>";
    }
    document.getElementById('task-modal').style.display = 'flex';
}
function openProjectModal(projectId) {
    const projects = window.projects;
    const selected = projects.find(p => p.id === projectId);
    const container = document.getElementById("project-requests-container");
    container.innerHTML = "";
    if (selected) {
        selected.requests.forEach(req => {
            let statusClass = '';
            if (req.accepted_by) statusClass = 'request-accepted';
            else if (req.rejected_by) statusClass = 'request-rejected';
            container.innerHTML += `
                <div class="border p-2 mb-2 ${statusClass}">
                    <strong>Action:</strong> ${req.action_type}<br>
                    <strong>Status:</strong> ${req.status}<br>
                    <strong>Reason:</strong> ${req.reason}<br>
                    <strong>Date:</strong> ${req.date}<br>
                    ${!req.accepted_by && !req.rejected_by ? `
                        <button class="btn btn-success btn-sm" onclick="handleRequestAction(${req.id}, 'accept')">Accept</button>
                        <button class="btn btn-danger btn-sm" onclick="handleRequestAction(${req.id}, 'reject')">Reject</button>
                    ` : ''}
                </div>
            `;
        });
        const bsModal = new bootstrap.Modal(document.getElementById('projectModal'));
        bsModal.show();
    } else {
        container.innerHTML = "<p>No requests found for this project.</p>";
    }
}
function closeTaskModal() {
    document.getElementById('task-modal').style.display = 'none';
}
function openSettingsModal() {
    const taskId = document.getElementById('modal-task-id').value;
    if (!taskId) {
        alert('No task selected.');
        return;
    }
    const bsModal = new bootstrap.Modal(document.getElementById('settingsModal'));
    bsModal.show();
}
let pendingAction = null;
let pendingRequestId = null;
let confirmModalInstance = null;
function handleRequestAction(requestId, action) {
    pendingRequestId = requestId;
    pendingAction = action;
    document.getElementById("confirmMessage").textContent =
        `Are you sure you want to ${action} this request?`;
    const confirmModal = new bootstrap.Modal(document.getElementById("confirmModal"));
    confirmModalInstance = confirmModal;
    confirmModal.show();
    const confirmBtn = document.getElementById("confirmActionBtn");
    confirmBtn.onclick = () => {
        confirmModalInstance.hide();
        const confirmEl = document.getElementById("confirmModal");
        confirmEl.addEventListener("hidden.bs.modal", function onHidden() {
            confirmEl.removeEventListener("hidden.bs.modal", onHidden);
            fetch(window.routes.handleRequestAction, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRF-Token": window.csrfToken
                },
                body: JSON.stringify({ request_id: pendingRequestId, action: pendingAction }),
            })
            .then(response => response.json().then(data => {
                console.log("Response data:", data);
                if (response.ok) {
                    if (pendingAction === 'accept') {
                        if (data.task_id) {
                            // Acción para tarea aceptada
                            fetch(window.routes.prepareEditTask, {
                                method: "POST",
                                headers: {
                                    "Content-Type": "application/json",
                                    "X-CSRF-Token": window.csrfToken
                                },
                                body: JSON.stringify({ task_id: data.task_id })
                            })
                            .then(res => res.json())
                            .then(prep => {
                                if (prep.success) {
                                    window.location.href = window.routes.editTask;
                                } else {
                                    document.getElementById("errorMessage").textContent = prep.error || "Could not prepare task for editing.";
                                    const errorModal = new bootstrap.Modal(document.getElementById("errorModal"));
                                    errorModal.show();
                                }
                            });
                        } else if (data.project_id) {
                            // Acción para proyecto aceptado
                            fetch(window.routes.prepareEditProject, {
                                method: "POST",
                                headers: {
                                    "Content-Type": "application/json",
                                    "X-CSRF-Token": window.csrfToken
                                },
                                body: JSON.stringify({ project_id: data.project_id })
                            })
                            .then(res => res.json())
                            .then(prep => {
                                if (prep.success) {
                                    window.location.href = window.routes.editProject; // Define esta ruta
                                } else {
                                    document.getElementById("errorMessage").textContent = prep.error || "Could not prepare project for editing.";
                                    const errorModal = new bootstrap.Modal(document.getElementById("errorModal"));
                                    errorModal.show();
                                }
                            });
                        } else {
                            // Si no hay task_id ni project_id, mostrar éxito genérico
                            document.getElementById("successMessage").textContent = `Request ${pendingAction}ed.`;
                            const successModal = new bootstrap.Modal(document.getElementById("successModal"));
                            successModal.show();
                        }
                    } else {
                        // Acción para reject o cualquier otro action
                        document.getElementById("successMessage").textContent = `Request ${pendingAction}ed.`;
                        const successModal = new bootstrap.Modal(document.getElementById("successModal"));
                        successModal.show();
                    }
                } else {
                    document.getElementById("errorMessage").textContent = data.error || "Something went wrong.";
                    const errorModal = new bootstrap.Modal(document.getElementById("errorModal"));
                    errorModal.show();
                }
            }))
            .catch(error => {
                console.error("Error:", error);
                document.getElementById("errorMessage").textContent = "Error sending request.";
                const errorModal = new bootstrap.Modal(document.getElementById("errorModal"));
                errorModal.show();
            });
        });
    };
}

let isCardView = true; // Estado global para la vista actual

function applyToggleView() {
    const taskContainers = document.querySelectorAll(".task-container");
    const tasks = document.querySelectorAll(".task-spacer");
    const taskElements = document.querySelectorAll(".task-element");
    const taskSubheaders = document.querySelectorAll(".task-subheader");
    const taskPriorities = document.querySelectorAll(".task-priority");
    const taskDueDates = document.querySelectorAll(".task-due-date");
    const toggleButton = document.getElementById("toggle-view");

    if (isCardView) {
        // Aplicar vista tarjeta (card-view)
        taskContainers.forEach(taskContainer => {
            taskContainer.classList.add("card-view", "row");
            taskContainer.classList.remove("list-view");
        });
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

    } else {
        // Aplicar vista lista (list-view)
        taskContainers.forEach(taskContainer => {
            taskContainer.classList.remove("card-view", "row");
            taskContainer.classList.add("list-view");
        });
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
        toggleButton.innerHTML = "view_module";
    }
}

function renderTasksAndProjects(data, typeId) {
    const container = document.getElementById("tasks-list");
    container.innerHTML = ""; 
    const tasks = Array.isArray(data.tasks) ? data.tasks : [];
    window.tasks = tasks;
    const projects = Array.isArray(data.projects_requests) ? data.projects_requests : [];
    window.projects = projects;

    const hasTasks = tasks.length > 0;
    const hasProjects = projects.length > 0;

    if (typeId === "1" && !hasProjects) {
        container.innerHTML = `
            <div class="alert alert-info mt-4" role="alert">
                No project requests found.
            </div>`;
        return;
    }

    if (typeId === "2" && !hasTasks) {
        container.innerHTML = `
            <div class="alert alert-info mt-4" role="alert">
                No task requests found.
            </div>`;
        return;
    }

    if ((typeId !== "1" && typeId !== "2") && !hasTasks && !hasProjects) {
        container.innerHTML = `
            <div class="alert alert-info mt-4" role="alert">
                No task or project requests found.
            </div>`;
        return;
    }

    const row = document.createElement("div");
    row.className = "task-container card-view row gx-5";

    if (typeId != 1) {
         for (let i = 0; i < tasks.length; i++) {
        const task = tasks[i];
        const col = document.createElement("div");
        col.className = "task-spacer col-3";
        col.innerHTML = `
                    <div class="task-item" data-task-id="${task.id}" onclick="openTaskModalFromCard(this)">
                        <h6 class="project-name">Project: ${task.project_name}</h6>
                        <h4 class="task-title">${task.title}</h4>
                        <div class="task-element task-subheader row">
                            <p class="priority col-4">
                                ${task.priority}
                                <span class="task-priority ${task.priority.toLowerCase()}"></span>
                            </p>
                            <div class="task-due-date col-8">
                                <span class="material-icons clock-icon">schedule</span>
                                <span class="due-date-text">${task.due_date}</span>
                            </div>
                        </div>
                        <p class="task-element task-description">${task.description}</p>
                        <div class="task-requirements">
                            ${task.requirements.map(req => `
                                <div style="display:flex">
                                    <label class="checkbox-container">
                                        <input class="custom-checkbox" type="checkbox" ${req.is_completed ? "checked" : ""}>
                                        <span class="checkmark"></span>
                                    </label>
                                    <label class="custom-checkbox-label">${req.requirement}</label>
                                </div>
                            `).join('')}
                        </div>
                    </div>
        `;
        row.appendChild(col);
    }
}

    if (typeId != 2) {
        projects.forEach(project => {
            const col = document.createElement("div");
            col.className = "task-spacer col-3";
            col.innerHTML = `
                <div class="task-item" onclick="openProjectModal(${project.id})">
                    <h6 class="project-name">Project: ${project.name}</h6>
                    <h4 class="task-title">Project Request</h4>
                    <div class="task-element task-subheader row">
                        <div class="task-due-date col-12">
                            <span class="material-icons clock-icon">event</span>
                            <span class="due-date-text">From: ${project.start_date || 'N/A'} to ${project.end_date || 'N/A'}</span>
                        </div>
                    </div>
                    <p class="task-element task-description">This project has pending requests.</p>
                </div>
            `;
            row.appendChild(col);
        });
    }

container.appendChild(row);

    applyToggleView();
}

document.addEventListener("DOMContentLoaded", () => {
    const dropdownMenu = document.querySelector('.requestmg-dropdown-menu');
    if (!dropdownMenu) return;

    const dropdownToggleButton = document.getElementById("requestmgTaskTypeDropdownButton");
    const bootstrapDropdown = bootstrap.Dropdown.getOrCreateInstance(dropdownToggleButton);

    const toggleButton = document.getElementById("toggle-view");
    toggleButton.addEventListener("click", () => {
        isCardView = !isCardView;
        applyToggleView();
    });

    dropdownMenu.addEventListener('click', async (event) => {
        event.preventDefault();
        event.stopPropagation();
        const item = event.target.closest('.requestmg-dropdown-project-item');
        if (!item) return;
        const selectedId = item.getAttribute('data-id');
        const selectedTypeName = item.textContent.trim();

        try {
            const response = await fetch(`/api/requests/filter?type_id=${selectedId}`);
            const data = await response.json();
            renderTasksAndProjects(data, selectedId);
            dropdownToggleButton.textContent = selectedTypeName;
            bootstrapDropdown.hide();
        } catch (e) {
            console.error("Error fetching filtered data:", e);
        }
    });
     const initialData = {
        tasks: window.tasks,
        projects_requests: window.projects
    };
    const initialTypeId = "{{ active_type.id }}";
    renderTasksAndProjects(initialData, initialTypeId);
});

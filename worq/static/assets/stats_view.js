document.addEventListener('DOMContentLoaded', () => {
    const taskStats = window.taskStatsData;
    if (!taskStats) return;

    // Calcular el total de tareas (por seguridad contra división por cero)
    const total = taskStats.assigned || 0;

    // Validar que haya datos
    if (total === 0) {
        document.getElementById('taskStatsChart').innerHTML = "<p>There are no tasks assigned to this project.</p>";
        return;
    }

    const series = [
        taskStats.completed,
        taskStats.late,
        taskStats.assigned
    ];
    const labels = ['Completed', 'Late', 'Pending'];


    new Chartist.Pie('#taskStatsChart', {
        labels: labels,
        series: series
    }, {
        showLabel: true,
        chartPadding: 20
    });
});

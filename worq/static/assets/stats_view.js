document.addEventListener('DOMContentLoaded', () => {
    const taskStats = window.taskStatsData;
    if (!taskStats) return;

    // Calcular el total de tareas (por seguridad contra división por cero)
    const total = taskStats.assigned || 0;

    // Validar que haya datos
    if (total === 0) {
        document.getElementById('taskStatsChart').innerHTML = "<p>No hay tareas asignadas para este proyecto.</p>";
        return;
    }

    const series = [
        taskStats.completed,
        taskStats.late,
        taskStats.assigned
    ];
    const labels = ['Completadas', 'Atrasadas', 'Pendientes'];


    new Chartist.Pie('#taskStatsChart', {
        labels: labels,
        series: series
    }, {
        donut: true,
        donutWidth: 130,
        showLabel: true,
        chartPadding: 20
    });
});

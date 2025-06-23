document.addEventListener('DOMContentLoaded', () => { 
    const taskStats = window.taskStatsData;
    if (!taskStats) return;

    const entries = [
        { label: 'Completed', value: taskStats.completed },
        { label: 'Late', value: taskStats.late },
        { label: 'Assigned', value: taskStats.assigned },
        { label: 'Delivered', value: taskStats.delivered }
    ];

    const filtered = entries.filter(e => e.value && e.value > 0);

    if (filtered.length === 0) {
        document.getElementById('taskStatsChart').innerHTML = "<p>There are no tasks assigned to this project.</p>";
        return;
    }

    const labels = filtered.map(e => e.label);
    const series = filtered.map(e => e.value);

    const chart = new Chartist.Pie('#taskStatsChart', {
        labels: labels,
        series: series
    }, {
        showLabel: true,
        chartPadding: 20
    });

    chart.on('draw', function(data) {
        if(data.type === 'slice') {
            const label = labels[data.index];
            const classMap = {
                'Completed': 'ct-completed',
                'Late': 'ct-late',
                'Assigned': 'ct-assigned',
                'Delivered': 'ct-delivered'
            };
            if(classMap[label]) {
                data.element.removeClass(`ct-series-${String.fromCharCode(97 + data.index)}`);
                data.element.addClass(classMap[label]);
                data.element._node.setAttribute('fill', {
                    'Completed': '#198754',
                    'Late': '#dc3545',
                    'Assigned': '#0dcaf0',
                    'Delivered': '#ffc107'
                }[label]);
            }
        }
    });
});

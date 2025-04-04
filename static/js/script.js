/* Custom JavaScript for NetReply intranet website */

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Initialize FullCalendar for attendance calendar
function initAttendanceCalendar(events) {
    var calendarEl = document.getElementById('attendance-calendar');
    if (!calendarEl) return;
    
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,listWeek'
        },
        events: events,
        eventClick: function(info) {
            // Show event details in modal
            var event = info.event;
            var props = event.extendedProps;
            
            var modalTitle = document.getElementById('eventModalTitle');
            var modalBody = document.getElementById('eventModalBody');
            
            if (modalTitle && modalBody) {
                modalTitle.textContent = event.title;
                
                var content = '<p><strong>Employee:</strong> ' + props.employee + '</p>';
                if (props.type === 'attendance') {
                    content += '<p><strong>Location:</strong> ' + props.location + '</p>';
                } else if (props.type === 'leave') {
                    content += '<p><strong>Status:</strong> ' + props.status + '</p>';
                    if (props.reason) {
                        content += '<p><strong>Reason:</strong> ' + props.reason + '</p>';
                    }
                }
                
                modalBody.innerHTML = content;
                
                var eventModal = new bootstrap.Modal(document.getElementById('eventModal'));
                eventModal.show();
            }
        }
    });
    
    calendar.render();
}

// Initialize FullCalendar for leave calendar
function initLeaveCalendar(events) {
    var calendarEl = document.getElementById('leave-calendar');
    if (!calendarEl) return;
    
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,listWeek'
        },
        events: events,
        eventClick: function(info) {
            // Show event details in modal
            var event = info.event;
            var props = event.extendedProps;
            
            var modalTitle = document.getElementById('eventModalTitle');
            var modalBody = document.getElementById('eventModalBody');
            
            if (modalTitle && modalBody) {
                modalTitle.textContent = event.title;
                
                var content = '<p><strong>Employee:</strong> ' + props.employee + '</p>';
                content += '<p><strong>Status:</strong> ' + props.status + '</p>';
                if (props.reason) {
                    content += '<p><strong>Reason:</strong> ' + props.reason + '</p>';
                }
                
                modalBody.innerHTML = content;
                
                var eventModal = new bootstrap.Modal(document.getElementById('eventModal'));
                eventModal.show();
            }
        }
    });
    
    calendar.render();
}

// Initialize FullCalendar for combined calendar
function initCombinedCalendar(events) {
    var calendarEl = document.getElementById('combined-calendar');
    if (!calendarEl) return;
    
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,listWeek'
        },
        events: events,
        eventClick: function(info) {
            // Show event details in modal
            var event = info.event;
            var props = event.extendedProps;
            
            var modalTitle = document.getElementById('eventModalTitle');
            var modalBody = document.getElementById('eventModalBody');
            
            if (modalTitle && modalBody) {
                modalTitle.textContent = event.title;
                
                var content = '<p><strong>Employee:</strong> ' + props.employee + '</p>';
                if (props.type === 'attendance') {
                    content += '<p><strong>Location:</strong> ' + props.location + '</p>';
                } else if (props.type === 'leave') {
                    content += '<p><strong>Status:</strong> ' + props.status + '</p>';
                    if (props.reason) {
                        content += '<p><strong>Reason:</strong> ' + props.reason + '</p>';
                    }
                }
                
                modalBody.innerHTML = content;
                
                var eventModal = new bootstrap.Modal(document.getElementById('eventModal'));
                eventModal.show();
            }
        }
    });
    
    calendar.render();
}

// Initialize charts for reports
function initAttendanceChart(data) {
    var ctx = document.getElementById('attendanceChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Attendance Count',
                data: data.values,
                backgroundColor: 'rgba(23, 162, 184, 0.5)',
                borderColor: 'rgba(23, 162, 184, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

function initLeaveChart(data) {
    var ctx = document.getElementById('leaveChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: [
                    'rgba(40, 167, 69, 0.5)',
                    'rgba(255, 193, 7, 0.5)',
                    'rgba(220, 53, 69, 0.5)'
                ],
                borderColor: [
                    'rgba(40, 167, 69, 1)',
                    'rgba(255, 193, 7, 1)',
                    'rgba(220, 53, 69, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Handle notification read status
function markNotificationRead(notificationId) {
    fetch('/notifications/' + notificationId + '/mark-read/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.ok) {
            var notification = document.getElementById('notification-' + notificationId);
            if (notification) {
                notification.classList.remove('unread');
            }
        }
    });
}

// Helper function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

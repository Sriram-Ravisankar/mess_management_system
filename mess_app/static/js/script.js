function renderIcons() {
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // --- Setup Elements ---
    const sidebar = document.getElementById('sidebar');
    const menuButton = document.getElementById('menu-btn');
    const navLinks = document.querySelectorAll('.nav-item');
    const appModules = document.querySelectorAll('.app-module');
    const pageTitle = document.getElementById('page-title');
    const backdrop = document.getElementById('backdrop');

    // --- Real-time Polling Elements ---
    const billAmount = document.getElementById('bill-amount');
    const billDueDate = document.getElementById('bill-due-date');
    const billStatus = document.getElementById('bill-status');
    const notificationsList = document.getElementById('notifications-list');
    const leaveSummary = document.getElementById('leave-summary');
    const leaveCard = document.getElementById('leave-card'); 


    // --- Mobile Menu Toggle ---
    function toggleSidebar() {
        sidebar.classList.toggle('-translate-x-full');
        backdrop.classList.toggle('hidden');
        document.body.classList.toggle('overflow-hidden', !sidebar.classList.contains('-translate-x-full'));
    }

    menuButton.addEventListener('click', toggleSidebar);
    backdrop.addEventListener('click', toggleSidebar);

    // --- Real-time Polling Logic ---
    const updateDashboardData = async () => {
        const endpointUrl = window.location.origin + '/data-endpoint/'; 
        try {
            const response = await fetch(endpointUrl);
            if (!response.ok) throw new Error('Network response was not ok.');
            
            const data = await response.json();
            const dash = data.dashboard;

            // 1. Update Bill Card
            if (dash.bill) {
                billAmount.textContent = `₹${dash.bill.amount}`;
                billDueDate.textContent = dash.bill.due_date;
                billStatus.textContent = `(${dash.bill.status})`;
                
                // Update color based on status code
                billStatus.classList.remove('text-red-600', 'text-green-600');
                billStatus.classList.add(dash.bill.status_code === 'D' ? 'text-red-600' : 'text-green-600');
                
                // Update card border color based on status
                const billCard = document.getElementById('bill-card');
                billCard.classList.remove('border-red-600', 'border-indigo-600', 'border-green-600');
                
                if (dash.bill.status_code === 'D') {
                    billCard.classList.add('border-red-600');
                } else if (dash.bill.status_code === 'P') {
                    // Use green for paid/resolved status
                    billCard.classList.add('border-green-600'); 
                } else {
                    // Fallback for unexpected status
                    billCard.classList.add('border-indigo-600');
                }
            }

            // 2. Update Leave Status Card
            const leaveCount = dash.pending_leaves;
            const latestStatus = dash.latest_leave_status;

            if (leaveCount > 0) {
                leaveSummary.innerHTML = `<span class="text-amber-600">${leaveCount} Pending Requests</span>`;
                leaveCard.classList.remove('border-green-500', 'border-red-500');
                leaveCard.classList.add('border-amber-500');
            } else if (latestStatus === 'A') {
                leaveSummary.innerHTML = `<span class="text-green-600">Latest: Approved</span>`;
                leaveCard.classList.remove('border-amber-500', 'border-red-500');
                leaveCard.classList.add('border-green-500');
            } else if (latestStatus === 'R') {
                leaveSummary.innerHTML = `<span class="text-red-600">Latest: Rejected</span>`;
                leaveCard.classList.remove('border-amber-500', 'border-green-500');
                leaveCard.classList.add('border-red-500'); 
            } else {
                leaveSummary.innerHTML = `<span class="text-gray-600">All Resolved / No Requests</span>`;
                leaveCard.classList.remove('border-amber-500', 'border-green-500');
                leaveCard.classList.add('border-gray-500');
            }

            // 3. Update Notifications
            notificationsList.innerHTML = '';
            if (dash.notifications.length > 0) {
                dash.notifications.forEach(notif => {
                    const item = document.createElement('div');
                    item.className = 'p-3 bg-gray-50 rounded-lg border border-gray-200 text-sm font-medium';
                    item.innerHTML = `
                        <span class="text-indigo-600 mr-2">[Admin Alert]</span>
                        ${notif.message}
                        <span class="text-xs text-gray-500 ml-2 float-right">${notif.date}</span>
                    `;
                    notificationsList.appendChild(item);
                });
            } else {
                notificationsList.innerHTML = '<p class="text-center text-gray-500 py-2">No active announcements from the administration.</p>';
            }
            
            renderIcons();

        } catch (error) {
            console.error('Polling failed:', error);
        }
    };

    // Start polling every 10 seconds (10000 ms)
    setInterval(updateDashboardData, 10000);
    updateDashboardData();


    // --- Module Switching ---
    function switchModule(moduleName) {
        // 1. Hide all modules
        appModules.forEach(module => {
            module.classList.add('hidden');
        });
        
        // 2. Show the selected module and set title
        const activeModule = document.getElementById(moduleName + '-module');
        if (activeModule) {
            activeModule.classList.remove('hidden');
            
            const moduleTitleElement = activeModule.querySelector('h2');
            if (moduleTitleElement) {
                pageTitle.textContent = moduleTitleElement.textContent;
            } 
        }

        // 3. Update active link style 
        navLinks.forEach(link => {
            link.classList.remove('active-module');
        });

        const activeLink = document.querySelector(`.nav-item[data-module="${moduleName}"]`);
        if (activeLink) {
            activeLink.classList.add('active-module');
        }
        
        // 4. Update URL query parameter
        const newUrl = new URL(window.location);
        if (moduleName !== 'dashboard') {
            newUrl.searchParams.set('module', moduleName);
        } else {
            newUrl.searchParams.delete('module');
        }
        window.history.pushState({}, '', newUrl);

        // 5. Re-render icons after DOM manipulation 
        renderIcons();
    }
    
    // --- Event Listeners for Navigation ---
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const moduleName = link.getAttribute('data-module');
            switchModule(moduleName);
            
            // Close sidebar on mobile after clicking a link
            if (window.innerWidth < 768) {
                toggleSidebar();
            }
        });
    });

    // --- Initial State Setup ---
    const urlParams = new URLSearchParams(window.location.search);
    const initialModule = urlParams.get('module') || 'dashboard';
    
    // Initial app setup
    setTimeout(() => {
        switchModule(initialModule);
        renderIcons(); 
    }, 0); 
    
    // --- Form Styling Initialization (Run once after initial DOM is ready) ---
    const formFields = document.querySelectorAll('.form-field-wrapper input:not([type="submit"]):not([type="radio"]):not([type="checkbox"]), .form-field-wrapper textarea, .form-field-wrapper select');
    formFields.forEach(input => {
        input.classList.add('w-full', 'px-3', 'py-2', 'border', 'border-gray-300', 'rounded-lg', 'shadow-sm', 'focus:ring-indigo-500', 'focus:border-indigo-500', 'transition', 'text-sm');
    
    });
});

// Auto-dismiss Django Messages
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('#django-messages-container > div, .mb-6 > div');

    messages.forEach(function(msg) {
        setTimeout(function() {
            msg.style.transition = "opacity 1s ease, transform 1s ease";
            msg.style.opacity = "0";
            msg.style.transform = "translateY(-10px)"; // Optional: adds a slight slide-up effect

            setTimeout(function() {
                msg.remove();
            }, 1000);
        }, 3000); // 3 seconds visible
    });
});
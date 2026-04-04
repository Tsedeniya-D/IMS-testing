// Session timeout warning for admin interface
(function() {
    'use strict';
    
    // Only run on admin pages
    if (!window.location.pathname.startsWith('/secure-admin/')) {
        return;
    }
    
    // Get session timeout from Django context (if available)
    const sessionTimeout = 15 * 60; // 15 minutes in seconds
    const warningTime = 2 * 60; // Show warning 2 minutes before expiry
    
    let warningShown = false;
    let timeoutId;
    let warningId;
    
    function showSessionWarning() {
        if (warningShown) return;
        
        warningShown = true;
        
        // Create warning modal
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        `;
        
        modal.innerHTML = `
            <div style="background: white; padding: 30px; border-radius: 8px; max-width: 400px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
                <h3 style="margin: 0 0 15px; color: #dc2626;">⚠️ Session Expiring Soon</h3>
                <p style="margin: 0 0 20px; color: #6b7280;">Your session will expire in 2 minutes due to inactivity. Would you like to extend your session?</p>
                <div style="display: flex; gap: 10px; justify-content: center;">
                    <button id="extend-session" style="padding: 8px 16px; background: #059669; color: white; border: none; border-radius: 4px; cursor: pointer;">Extend Session</button>
                    <button id="logout-now" style="padding: 8px 16px; background: #dc2626; color: white; border: none; border-radius: 4px; cursor: pointer;">Log Out Now</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Handle button clicks
        document.getElementById('extend-session').addEventListener('click', function() {
            // Make a request to extend the session
            fetch(window.location.href, {method: 'HEAD'})
                .then(() => {
                    resetSessionTimer();
                    document.body.removeChild(modal);
                    warningShown = false;
                })
                .catch(() => {
                    // If request fails, just remove modal and reset
                    document.body.removeChild(modal);
                    warningShown = false;
                    resetSessionTimer();
                });
        });
        
        document.getElementById('logout-now').addEventListener('click', function() {
            window.location.href = '/secure-admin/logout/';
        });
    }
    
    function resetSessionTimer() {
        clearTimeout(timeoutId);
        clearTimeout(warningId);
        
        // Set warning timer
        warningId = setTimeout(showSessionWarning, (sessionTimeout - warningTime) * 1000);
        
        // Set logout timer (redirect to login)
        timeoutId = setTimeout(() => {
            window.location.href = '/accounts/login/?session=expired';
        }, sessionTimeout * 1000);
    }
    
    function startSessionTimer() {
        resetSessionTimer();
        
        // Reset timer on user activity
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
        events.forEach(event => {
            document.addEventListener(event, resetSessionTimer, true);
        });
    }
    
    // Start the timer when page loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', startSessionTimer);
    } else {
        startSessionTimer();
    }
    
})();

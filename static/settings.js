// settings.js - Complete centralized settings system for MCQ Game

// Add settings HTML to any page
function addSettingsToPage() {
    const settingsHTML = `
        <!-- Hamburger Menu -->
        <div class="hamburger-menu" onclick="toggleSidebar()">
            <div class="hamburger-line"></div>
            <div class="hamburger-line"></div>
            <div class="hamburger-line"></div>
        </div>

        <!-- Sidebar Menu -->
        <div class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <h3>Menu</h3>
                <div class="sidebar-close" onclick="closeSidebar()">×</div>
            </div>
            <div class="sidebar-content">
                <a href="/profile" class="sidebar-item">🏠 Home</a>
                <a href="/leaderboard" class="sidebar-item">🏆 Leaderboard</a>
                <a href="/account" class="sidebar-item">👤 Account</a>
                <a href="/logout" class="sidebar-item logout-item">🚪 Logout</a>
            </div>
        </div>

        <!-- Sidebar Overlay -->
        <div class="sidebar-overlay" id="sidebarOverlay" onclick="closeSidebar()"></div>

        <!-- Settings Dropdown -->
        <div class="settings-dropdown">
            <div class="settings-icon" onclick="toggleSettings()">⚙️</div>
            <div class="settings-menu" id="settingsMenu">
                <div class="settings-item" onclick="sendFeedback()">📧 Feedback</div>
                <div class="settings-item" onclick="toggleDarkMode()">
                    <span id="darkModeIcon">🌙</span> <span id="darkModeText">Dark Mode</span>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('afterbegin', settingsHTML);
}

// Add settings CSS to any page
function addSettingsCSS() {
    const settingsCSS = `
        <style>
        /* Hamburger Menu Styles */
        .hamburger-menu {
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 1002;
            width: 30px;
            height: 30px;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            justify-content: space-around;
            padding: 5px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 5px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
        }

        .hamburger-menu:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: scale(1.05);
        }

        .hamburger-line {
            width: 100%;
            height: 3px;
            background: white;
            border-radius: 2px;
            transition: all 0.3s ease;
        }

        .hamburger-menu:hover .hamburger-line {
            background: rgba(255, 255, 255, 0.9);
        }

        /* Sidebar Styles */
        .sidebar {
            position: fixed;
            top: 0;
            left: -300px;
            width: 280px;
            height: 100vh;
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(15px);
            border-right: 1px solid rgba(255, 255, 255, 0.2);
            z-index: 1001;
            transition: left 0.3s ease;
            box-shadow: 2px 0 20px rgba(0, 0, 0, 0.1);
        }

        .sidebar.open {
            left: 0;
        }

        .sidebar-header {
            padding: 25px 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .sidebar-header h3 {
            margin: 0;
            color: white;
            font-size: 1.5em;
            font-weight: 300;
        }

        .sidebar-close {
            font-size: 2em;
            color: white;
            cursor: pointer;
            opacity: 0.7;
            transition: opacity 0.2s ease;
        }

        .sidebar-close:hover {
            opacity: 1;
        }

        .sidebar-content {
            padding: 20px 0;
        }

        .sidebar-item {
            display: block;
            padding: 15px 25px;
            color: white;
            text-decoration: none;
            transition: all 0.2s ease;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            font-size: 1.1em;
        }

        .sidebar-item:hover {
            background: rgba(255, 255, 255, 0.1);
            padding-left: 35px;
        }

        .sidebar-item.logout-item {
            margin-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.2);
            color: rgba(255, 100, 100, 0.9);
        }

        .sidebar-item.logout-item:hover {
            background: rgba(255, 100, 100, 0.1);
        }

        .sidebar-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.3);
            z-index: 1000;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
        }

        .sidebar-overlay.active {
            opacity: 1;
            visibility: visible;
        }

        /* Settings Dropdown Styles */
        .settings-dropdown {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1002;
        }

        .settings-icon {
            width: 45px;
            height: 45px;
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2em;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }

        .settings-icon:hover {
            background: rgba(255, 255, 255, 0.25);
            transform: rotate(90deg) scale(1.1);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
        }

        .settings-menu {
            position: absolute;
            top: 55px;
            right: 0;
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            min-width: 160px;
            display: none;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            animation: slideDown 0.3s ease;
        }

        .settings-menu.show {
            display: block;
        }

        .settings-item {
            padding: 12px 16px;
            cursor: pointer;
            transition: background 0.2s ease;
            color: white;
            border-radius: 8px;
            margin: 5px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .settings-item:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* Dark Mode Styles */
        body.dark-mode {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
        }

        body.dark-mode .container,
        body.dark-mode .profile-section,
        body.dark-mode .stat-card,
        body.dark-mode .recent-games,
        body.dark-mode .header,
        body.dark-mode .question,
        body.dark-mode .loading-container,
        body.dark-mode .sidebar {
            background: rgba(0, 0, 0, 0.3) !important;
            border-color: rgba(255, 255, 255, 0.1) !important;
        }

        body.dark-mode .settings-icon,
        body.dark-mode .settings-menu {
            background: rgba(0, 0, 0, 0.4) !important;
            border-color: rgba(255, 255, 255, 0.15) !important;
        }

        body.dark-mode .settings-item:hover,
        body.dark-mode .sidebar-item:hover {
            background: rgba(255, 255, 255, 0.05) !important;
        }

        body.dark-mode input,
        body.dark-mode button {
            background: rgba(0, 0, 0, 0.2) !important;
            border-color: rgba(255, 255, 255, 0.2) !important;
        }

        body.dark-mode input:focus,
        body.dark-mode button:hover:not(.question button) {
            background: rgba(0, 0, 0, 0.3) !important;
        }

        /* Allow answer highlighting to work in dark mode */
        body.dark-mode .question button[style*="lightgreen"] {
            background: lightgreen !important;
            color: white !important;
        }

        body.dark-mode .question button[style*="salmon"] {
            background: salmon !important;
            color: white !important;
        }
        </style>
    `;
    
    document.head.insertAdjacentHTML('beforeend', settingsCSS);
}

// Settings functionality
function toggleSettings() {
    const menu = document.getElementById('settingsMenu');
    menu.classList.toggle('show');
}

function closeSettings() {
    const menu = document.getElementById('settingsMenu');
    if (menu) menu.classList.remove('show');
}

// Sidebar functionality
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    
    sidebar.classList.add('open');
    overlay.classList.add('active');
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
}

function sendFeedback() {
    const subject = 'MCQ Game Feedback';
    const body = 'Hi,\n\nI would like to share the following feedback about the MCQ Game:\n\n';
    const mailtoLink = `mailto:grim98413@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    
    window.location.href = mailtoLink;
    closeSettings();
}

function toggleDarkMode() {
    const body = document.body;
    const icon = document.getElementById('darkModeIcon');
    const text = document.getElementById('darkModeText');
    
    if (!icon || !text) return;
    
    body.classList.toggle('dark-mode');
    
    if (body.classList.contains('dark-mode')) {
        icon.textContent = '☀️';
        text.textContent = 'Light Mode';
        localStorage.setItem('darkMode', 'enabled');
    } else {
        icon.textContent = '🌙';
        text.textContent = 'Dark Mode';
        localStorage.setItem('darkMode', 'disabled');
    }
    
    closeSettings();
}

// Initialize settings system
function initializeSettings() {
    // Add CSS and HTML to page
    addSettingsCSS();
    addSettingsToPage();
    
    // Load saved dark mode preference
    if (localStorage.getItem('darkMode') === 'enabled') {
        document.body.classList.add('dark-mode');
        const icon = document.getElementById('darkModeIcon');
        const text = document.getElementById('darkModeText');
        if (icon && text) {
            icon.textContent = '☀️';
            text.textContent = 'Light Mode';
        }
    }
    
    // Close settings when clicking outside
    document.addEventListener('click', function(event) {
        const settingsDropdown = document.querySelector('.settings-dropdown');
        const sidebar = document.querySelector('.sidebar');
        
        // Close settings if clicked outside
        if (settingsDropdown && !settingsDropdown.contains(event.target)) {
            closeSettings();
        }
        
        // Close sidebar if clicked on overlay
        if (event.target.classList.contains('sidebar-overlay')) {
            closeSidebar();
        }
    });

    // Handle keyboard events
    document.addEventListener('keydown', function(event) {
        // Close sidebar on Escape key
        if (event.key === 'Escape') {
            closeSidebar();
            closeSettings();
        }
    });
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeSettings);
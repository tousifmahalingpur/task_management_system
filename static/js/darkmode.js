// =========================
// LOAD SAVED THEME
// =========================

document.addEventListener("DOMContentLoaded", () => {

    const savedTheme = localStorage.getItem("theme");

    if (savedTheme === "dark") {

        document.body.classList.add("dark-mode");

        updateButton(true);

    } else {

        updateButton(false);

    }

});

// =========================
// TOGGLE DARK MODE
// =========================

function toggleDarkMode() {

    document.body.classList.toggle("dark-mode");

    const isDark =
        document.body.classList.contains("dark-mode");

    if (isDark) {

        localStorage.setItem("theme", "dark");

    } else {

        localStorage.setItem("theme", "light");

    }

    updateButton(isDark);
}

// =========================
// UPDATE BUTTON TEXT
// =========================

function updateButton(isDark) {

    const btn =
        document.getElementById("darkModeToggle");

    if (!btn) return;

    if (isDark) {

        btn.innerHTML = "☀ Light Mode";

    } else {

        btn.innerHTML = "🌙 Dark Mode";

    }
}
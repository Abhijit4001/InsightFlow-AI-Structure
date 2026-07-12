const themeButtons = document.querySelectorAll("[data-theme-toggle]");
let currentTheme = document.documentElement.getAttribute("data-theme") || "dark";

function applyTheme(theme) {
  currentTheme = theme;
  document.documentElement.setAttribute("data-theme", theme);

  themeButtons.forEach((btn) => {
    btn.setAttribute(
      "aria-label",
      theme === "dark" ? "Switch to light mode" : "Switch to dark mode"
    );
    const icon = btn.querySelector(".theme-icon");
    if (icon) {
      icon.textContent = theme === "dark" ? "◐" : "◑";
    }
  });
}

function toggleTheme() {
  applyTheme(currentTheme === "dark" ? "light" : "dark");
}

themeButtons.forEach((btn) => btn.addEventListener("click", toggleTheme));
applyTheme(currentTheme);

const landingFileInput = document.getElementById("landing-file");
const landingFileName = document.getElementById("landingFileName");
const landingStatus = document.getElementById("landingStatus");
const landingContinueBtn = document.getElementById("landingContinueBtn");
const landingDropzone = document.getElementById("landingDropzone");

function setLandingFile(file) {
  if (!file) {
    landingFileName.textContent = "No file selected";
    landingStatus.textContent = "Waiting for upload";
    landingContinueBtn.disabled = true;
    return;
  }

  landingFileName.textContent = file.name;
  landingStatus.textContent = "Ready to continue";
  landingContinueBtn.disabled = false;
  window.__selectedDatasetFile = file;
}

if (landingFileInput) {
  landingFileInput.addEventListener("change", (event) => {
    const file = event.target.files[0];
    setLandingFile(file);
  });
}

if (landingDropzone) {
  ["dragenter", "dragover"].forEach((eventName) => {
    landingDropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      landingDropzone.style.borderColor = "rgba(110, 231, 249, 0.7)";
      landingDropzone.style.background = "rgba(110, 231, 249, 0.08)";
    });
  });

  ["dragleave", "drop"].forEach((eventName) => {
    landingDropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      landingDropzone.style.borderColor = "rgba(110, 231, 249, 0.28)";
      landingDropzone.style.background = "";
    });
  });

  landingDropzone.addEventListener("drop", (e) => {
    const file = e.dataTransfer.files[0];
    if (file) {
      landingFileInput.files = e.dataTransfer.files;
      setLandingFile(file);
    }
  });
}

if (landingContinueBtn) {
  landingContinueBtn.addEventListener("click", () => {
    if (!window.__selectedDatasetFile) return;

    window.__dashboardBootFile = window.__selectedDatasetFile;
    sessionStorage.setItem("insightflow-file-name", window.__selectedDatasetFile.name);
    window.location.href = "./dashboard.html";
  });
}
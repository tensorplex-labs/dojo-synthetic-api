async function loadTrials() {
  try {
    const response = await fetch("commons/model_lab/syn-gen-trials.json");
    const data = await response.json();
    window.trialsData = data; // Store data in global scope for easy access
    console.log("Trials data loaded successfully");
  } catch (error) {
    console.error("Error loading trials:", error);
  }
}

// Load trials when the page loads
document.addEventListener("DOMContentLoaded", loadTrials);

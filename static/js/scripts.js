// scripts.js

document.addEventListener("DOMContentLoaded", () => {
  const slideMenu = document.getElementById("slidemenu");
  const dashboardHeading = document.querySelector("h1"); // The "Dashboard" h1

  // Initially, menu is visible
  let menuVisible = true;

  // Add click event to toggle sidebar
  dashboardHeading.style.cursor = "pointer"; // Show pointer on hover
  dashboardHeading.addEventListener("click", () => {
    if (menuVisible) {
      // Hide menu
      slideMenu.style.transform = "translateX(-120%)";
      menuVisible = false;
    } else {
      // Show menu
      slideMenu.style.transform = "translateX(0)";
      menuVisible = true;
    }
  });

  // Smooth transition for sliding
  slideMenu.style.transition = "transform 0.3s ease-in-out";
});

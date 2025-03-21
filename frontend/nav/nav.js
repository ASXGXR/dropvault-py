// ADDS NAV BAR
const navbarElement = document.getElementById('navbar');

fetch('nav/nav.html')
  .then(response => response.text())
  .then(data => {
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = data;

    // Append any <style> tags from nav.html to <head>
    tempDiv.querySelectorAll('style').forEach(styleEl => {
      document.head.appendChild(styleEl);
    });

    // Inject full nav HTML into #navbar
    navbarElement.innerHTML = tempDiv.innerHTML;

    // Select elements
    const nav = navbarElement;
    const navButtons = nav.querySelector('.nav-buttons');
    const navItems = navButtons.querySelectorAll('.nav-btn');

    // Get hamburger from main HTML (outside nav)
    const hamburger = document.querySelector('.hamburger');

    // Highlight current page
    const currentPath = window.location.pathname;
    navItems.forEach(navItem => {
      let itemPath = navItem.tagName.toLowerCase() === 'a' ? navItem.getAttribute('href') : null;
      if (itemPath && (itemPath.startsWith('http') || itemPath.startsWith('//'))) {
        itemPath = new URL(itemPath, window.location.origin).pathname;
      }
      if (itemPath === currentPath) {
        navItem.classList.add('active-nav-item');
      }
    });

    // Toggle nav on hamburger click
    hamburger.addEventListener('click', () => {
      hamburger.classList.toggle('hamburger--open');
      nav.classList.toggle('nav--open');
    });

    // Close nav on mobile after clicking a nav button
    navItems.forEach(navItem => {
      navItem.addEventListener('click', () => {
        hamburger.classList.remove('hamburger--open');
        nav.classList.remove('nav--open');
      });
    });
  });
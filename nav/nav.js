// ADDS NAV BAR
const navbarElement = document.getElementById('navbar');
fetch('nav/nav.html')
  .then(response => response.text())
  .then(data => {
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = data;
    const navElement = tempDiv.querySelector('nav');
    navbarElement.innerHTML = navElement ? navElement.innerHTML : data;

    // Append any <style> elements (outside <nav>) to the document head
    tempDiv.querySelectorAll('style').forEach(styleEl => {
      document.head.appendChild(styleEl);
    });

    const navButtons = navbarElement.querySelector('.nav-buttons');

    // HIGHLIGHT PAGE USER IS ON
    const currentPath = window.location.pathname;
    const navItems = navButtons.querySelectorAll('.nav-btn');
    navItems.forEach(navItem => {
      let itemPath = navItem.tagName.toLowerCase() === 'a' ? navItem.getAttribute('href') : null;
      if (itemPath && (itemPath.startsWith('http') || itemPath.startsWith('//'))) {
        itemPath = new URL(itemPath, window.location.origin).pathname;
      }
      if (itemPath === currentPath) {
        navItem.classList.add('active-nav-item');
      }
    });

    // ADD CLICK EVENT LISTENERS
    navItems.forEach(navItem => {
      if (navItem.tagName.toLowerCase() === 'button') {
        const page = navItem.getAttribute('data-page');
        if (page) {
          navItem.addEventListener('click', () => {
            window.location.href = page;
          });
        }
      }
    });

    // HAMBURGER CODE
    const hamburger = document.querySelector('.hamburger');
    hamburger.addEventListener('click', () => {
      hamburger.classList.toggle('hamburger--open');
      navButtons.classList.toggle('nav-buttons--open');
    });

    // Close nav-buttons on click (Mobile)
    navItems.forEach(navItem => {
      navItem.addEventListener('click', () => {
        navButtons.classList.remove('nav-buttons--open');
        hamburger.classList.remove('hamburger--open');
      });
    });
  });
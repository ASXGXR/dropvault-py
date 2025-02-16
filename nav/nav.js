// nav.js


// ADDS NAV BAR
const navbarElement = document.getElementById('navbar');
fetch('nav/nav.html')
.then(response => response.text())
.then(data => {
  navbarElement.innerHTML = data;

  const navButtons = navbarElement.querySelector('.nav-buttons');

  // Check if not on the main page
  // if (!window.location.href.endsWith('/brac-website/') && window.location.pathname !== '/') {
  //   navButtons.insertAdjacentHTML('afterbegin', `
  //     <a href="https://asxgxr.github.io/brac-website" class="nav-btn english-txt">HOME</a>
  //   `);
  // }

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
      // If page is null, do not add a click listener
    }
  });



  // NAV SCROLL HIDE

  // const scrollThreshold = 5; // scroll amt before hiding

  // let lastScrollTop = 0; //start from 0
  // const root = document.documentElement;
  // const nav = navbarElement.querySelector('nav');
  // const navHeight = getComputedStyle(root).getPropertyValue('--nav-height');
  // let ticking = false;
  // window.addEventListener('scroll', () => {
  //   if (!ticking) {
  //     window.requestAnimationFrame(() => {
  //       let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  //       if (scrollTop > lastScrollTop + scrollThreshold) {
  //         nav.style.top = `-${navHeight}`; // Hide nav
  //       } else if (scrollTop < lastScrollTop) {
  //         nav.style.top = '0'; // Show nav
  //       }
  //       lastScrollTop = Math.max(scrollTop, 0); // For mobile devices / negative scrolling
  //       ticking = false;
  //     });
  //     ticking = true; // Ensures one update per frame
  //   }
  // });


  // HAMBURGER CODE
  const hamburger = document.querySelector('.hamburger');
  hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('hamburger--open');
    navButtons.classList.toggle('nav-buttons--open');
  });


  // Close nav-buttons on click (Mobile)
  navItems.forEach(navItem => {
    navItem.addEventListener('click', () => {
      navButtons.classList.remove('nav-buttons--open'); // Close the nav menu
      hamburger.classList.remove('hamburger--open'); // Reset the hamburger icon
    });
  });



});
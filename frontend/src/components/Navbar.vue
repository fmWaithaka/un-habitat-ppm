<template>
  <nav class="navbar">
    <div class="navbar-brand">
      <router-link to="/" class="brand-link">
        <img src="/un-logo-white.png" alt="UN Logo" class="brand-logo" @error="logoError"/>
        <span class="brand-text">Project Portfolio</span>
      </router-link>
    </div>

    <ul class="navbar-links">
      <li>
        <router-link to="/" class="nav-link" active-class="active-link">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
          <span>Projects</span>
        </router-link>
      </li>
      <li>
        <router-link to="/dashboard" class="nav-link" active-class="active-link">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"></path><path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"></path></svg>
          <span>Dashboard</span>
        </router-link>
      </li>
      </ul>
  </nav>
</template>

<script setup>
// No specific script logic needed for Navbar.vue in this phase,
// other than the logo error handling.

// Function to handle logo loading error
const logoError = (event) => {
  // Hide the image element if it fails to load
  event.target.style.display = 'none';
  // Optionally, create and insert fallback text or a default icon
  const fallback = document.createElement('span');
  fallback.textContent = 'UN'; // Fallback text
  fallback.className = 'brand-text-fallback'; // Apply a class for styling
  // Insert the fallback element after the image
  event.target.parentNode.insertBefore(fallback, event.target.nextSibling);
};
</script>

<style scoped>
/* Scoped styles specific to Navbar.vue */

/* Styles for the main navigation bar */
.navbar {
  /* Use CSS variables for background and text colors defined in global.css */
  background-color: var(--color-background-nav);
  color: var(--color-text-nav);
  padding: 0 25px; /* Adjusted padding on left/right */
  display: flex; /* Use flexbox for layout */
  justify-content: space-between; /* Space out the brand and links */
  align-items: center; /* Vertically align items */
  height: 70px; /* Increased height for better visual presence */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15); /* Add a subtle shadow below the navbar */
  position: sticky; /* Make navbar stick to the top when scrolling */
  top: 0; /* Position at the top */
  z-index: 1000; /* Ensure navbar stays on top of other content */
}

/* Styles for the brand section (logo and text) */
.navbar-brand {
  display: flex; /* Use flexbox to align logo and text */
  align-items: center; /* Vertically align logo and text */
}

/* Styles for the link wrapping the brand */
.brand-link {
  display: flex; /* Use flexbox to align logo and text within the link */
  align-items: center; /* Vertically align */
  text-decoration: none; /* Remove underline from link */
  color: var(--color-text-nav); /* Inherit text color from navbar */
}

/* Styles for the brand logo image */
.brand-logo {
  height: 35px; /* Adjusted logo size */
  margin-right: 12px; /* Space between logo and brand text */
  /* Consider adding a filter for better visibility if logo is dark on dark background: */
  /* filter: brightness(0) invert(1); */ /* Example: turns a dark logo white */
}

/* Styles for the brand text (site title) */
.brand-text {
  font-size: 1.6em; /* Adjusted font size */
  font-weight: 600; /* Bolder brand text */
  letter-spacing: 0.5px; /* Add slight letter spacing */
}

/* Style for fallback text if logo fails (optional) */
.brand-text-fallback {
  font-size: 1.6em;
  font-weight: 600;
  letter-spacing: 0.5px;
  color: var(--color-text-nav);
  margin-left: 10px;
}


/* Styles for the navigation links list */
.navbar-links {
  list-style: none; /* Remove default list bullets */
  padding: 0; /* Remove default padding */
  margin: 0; /* Remove default margin */
  display: flex; /* Use flexbox to arrange links horizontally */
  align-items: center; /* Vertically align links */
}

/* Styles for individual list items in the nav links */
.navbar-links li {
  margin-left: 25px; /* Space between navigation items */
}

/* Styles for the navigation links themselves */
.nav-link {
  /* Use CSS variables for text color defined in global.css */
  color: var(--color-text-nav-link);
  text-decoration: none; /* Remove underline from links */
  font-size: 1.05em; /* Slightly larger nav link text */
  padding: 10px 15px; /* Add padding for larger clickable area */
  border-radius: 6px; /* Add rounded corners to links */
  transition: background-color 0.2s ease-in-out, color 0.2s ease-in-out; /* Smooth transition on hover/active */
  display: flex; /* Use flexbox to align icon and text */
  align-items: center; /* Vertically align icon and text */
  gap: 8px; /* Space between icon and text */
}

/* Styles for navigation links on hover */
.nav-link:hover {
  background-color: var(--color-background-nav-hover); /* Use hover background color */
  color: var(--color-text-nav-hover); /* Use hover text color */
}

/* Styles for the active navigation link (matching the current route) */
.nav-link.active-link {
  /* Use CSS variables for background and text color defined in global.css */
  background-color: var(--color-primary); /* Highlight active link with primary color */
  color: var(--color-text-light); /* Use light text color on the primary background */
  font-weight: 500; /* Make active link text slightly bolder */
}

/* Styles for SVG icons within navigation links */
.nav-link svg {
  stroke-width: 2; /* Ensure icons have a consistent stroke width */
}
</style>

document.addEventListener("DOMContentLoaded", function () {
  try {
    const videos = document.querySelectorAll("video");

    if (!videos || videos.length === 0) return;

    videos.forEach((video) => {
      video.addEventListener("play", function () {
        videos.forEach((otherVideo) => {
          if (otherVideo !== video) {
            try {
              otherVideo.pause();
            } catch (e) {
              // ignore any pause errors for inaccessible elements
            }
          }
        });
      });
    });

    // Per-card overlay behaviour: tie .home-play-overlay to its card's video
    const cards = document.querySelectorAll('.collection-card');
    if (cards && cards.length) {
      let foundOverlay = false;
      cards.forEach((card) => {
        const video = card.querySelector('video');
        const overlay = card.querySelector('.home-play-overlay');
        if (!overlay) return; // nothing to do for this card
        foundOverlay = true;
        if (!video) return;

        // When overlay clicked, attempt to play the card video
        overlay.addEventListener('click', function (e) {
          try {
            e.preventDefault();
          } catch (e) {}
          try { video.play(); } catch (err) {}
        });

        // When the video plays, mark card and hide overlay via class
        video.addEventListener('play', function () {
          card.classList.add('is-playing');
          overlay.classList.add('hidden');
        });

        // When the video pauses or ends, remove class and show overlay
        function stopHandler() {
          card.classList.remove('is-playing');
          overlay.classList.remove('hidden');
        }
        video.addEventListener('pause', stopHandler);
        video.addEventListener('ended', stopHandler);
      });
      // If no overlays were found on any cards, do nothing further
      if (!foundOverlay) {
        // no-op
      }
    }
  } catch (err) {
    // Fail silently to avoid breaking non-video pages
  }
});

// Mobile navigation overlay toggling: explicit state control
document.addEventListener('DOMContentLoaded', function () {
  try {
    const toggle = document.getElementById('mobile-nav-toggle') || document.querySelector('.mobile-nav-toggle');
    const menu = document.getElementById('main-menu') || document.querySelector('.menu');
    const overlay = document.getElementById('mobile-nav-overlay') || document.querySelector('.mobile-nav-overlay');
    const closeBtn = menu ? menu.querySelector('.mobile-close-btn') : null;

    if (!toggle || !menu) return;

    function setOverlayState(isOpen) {
      if (!overlay) return;
      try {
        overlay.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
        // rely on CSS to show/hide when the '.open' class is present
        try { overlay.classList.toggle('open', !!isOpen); } catch (e) {}
      } catch (e) {}
    }

    toggle.addEventListener('click', function () {
      try {
        const isOpen = menu.classList.toggle('open');
        // update aria-expanded on the toggle for accessibility
        try { toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false'); } catch (e) {}
        setOverlayState(isOpen);
      } catch (e) {}
    });

    if (overlay) {
      overlay.addEventListener('click', function () {
        try {
          menu.classList.remove('open');
          try { toggle.setAttribute('aria-expanded', 'false'); } catch (e) {}
          // remove overlay open class; CSS controls visibility
          try { overlay.classList.remove('open'); } catch (e) {}
          setOverlayState(false);
        } catch (e) {}
      });
    }

    if (closeBtn) {
      closeBtn.addEventListener('click', function () {
        try {
          menu.classList.remove('open');
          try { toggle.setAttribute('aria-expanded', 'false'); } catch (e) {}
          try { overlay.classList.remove('open'); } catch (e) {}
          setOverlayState(false);
        } catch (e) {}
      });
    }
  } catch (err) {
    // fail silently
  }
});

// Cookie consent banner behavior (persisted)
document.addEventListener("DOMContentLoaded", function () {
  var banner = document.getElementById('cookie-consent-bar');
  var btn = document.querySelector('.cookie-accept-btn');
  if (!banner) return;

  try {
    var consent = null;
    try { consent = localStorage.getItem('ochre_cookie_consent'); } catch (e) { consent = null; }

    if (consent !== 'true') {
      try { banner.removeAttribute('hidden'); banner.setAttribute('aria-hidden', 'false'); } catch (e) {}
    }

    if (btn) {
      btn.addEventListener('click', function () {
        try { localStorage.setItem('ochre_cookie_consent', 'true'); } catch (e) {}

        /* remove focus before hiding */
        try { document.activeElement.blur(); } catch (e) {}

        /* hide banner */
        try { banner.style.display = 'none'; banner.removeAttribute('aria-hidden'); } catch (e) {}
      });
    }
  } catch (e) {
    console.warn('Cookie consent initialization failed', e);
  }
});

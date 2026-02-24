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

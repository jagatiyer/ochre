document.addEventListener('click', function (ev) {
  var btn = ev.target.closest && ev.target.closest('.home-play-overlay, .commercial-play-overlay');
  if (!btn) return;

  // Home inline playback
  var homeCard = btn.closest && btn.closest('.collection-card');
  if (homeCard) {
    var video = homeCard.querySelector('video');
    if (video) {
      var p = video.play();
      if (p && p.catch) {
        p.catch(function () {
          try { video.muted = true; video.play(); } catch (e) {}
        });
      }
    }
    return;
  }

  // Commercials: delegate to existing click handler by triggering card click,
  // then attempt to autoplay the modal video (muted fallback allowed).
  var commercialCard = btn.closest && btn.closest('.commercial-card');
  if (commercialCard) {
    // reuse existing handler
    commercialCard.click();

    // attempt to play the modal video once it is inserted
    setTimeout(function () {
      var modalVideo = document.querySelector('#videoModal video, #videoModal iframe');
      if (!modalVideo) return;
      try {
        if (modalVideo.tagName.toLowerCase() === 'video') {
          var p = modalVideo.play();
          if (p && p.catch) {
            p.catch(function () {
              try { modalVideo.muted = true; modalVideo.play(); } catch (e) {}
            });
          }
        } else if (modalVideo.tagName.toLowerCase() === 'iframe') {
          modalVideo.focus && modalVideo.focus();
        }
      } catch (e) {}
    }, 80);
  }
});

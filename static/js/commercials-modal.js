document.addEventListener('DOMContentLoaded', function () {
  // Debug: dump card data attributes for troubleshooting
  try {
    var debugCards = document.querySelectorAll('.commercials-grid .commercial-item, .commercials-grid .commercial-card, .commercial-card-link');
    debugCards.forEach(function (card, idx) {
      var ds = card.dataset || {};
      console.log('Card ' + idx + ':', {
        type: ds.type || null,
        url: ds.url || null,
        embedUrl: ds.embedUrl || ds.embedurl || null,
        title: ds.title || (card.querySelector && (card.querySelector('h3, h4') ? card.querySelector('h3, h4').textContent.trim() : null))
      });
    });
  } catch (e) {
    console.warn('commercials-modal debug dump failed', e);
  }

  // Helper: extract YouTube ID from various URL formats or iframe HTML
  function getYouTubeID(url) {
    if (!url) return null;
    var s = String(url).trim();
    // If iframe HTML was pasted, extract src
    var srcMatch = s.match(/src=["']([^"']+)["']/i);
    if (srcMatch) s = srcMatch[1];
    var m = s.match(/(?:v=|\/embed\/|youtu\.be\/)([A-Za-z0-9_-]{11})/);
    if (m && m[1]) return m[1];
    // direct id
    if (/^[A-Za-z0-9_-]{11}$/.test(s)) return s;
    return null;
  }

  // Build a consistent modal inside the dedicated root
  function removeExistingModal() {
    var root = document.getElementById('video-modal-root');
    if (!root) return;
    var oldOverlay = document.getElementById('video-overlay');
    var oldModal = document.getElementById('videoModal');
    if (oldOverlay && oldOverlay.parentNode) oldOverlay.parentNode.removeChild(oldOverlay);
    if (oldModal && oldModal.parentNode) oldModal.parentNode.removeChild(oldModal);
    try {
      if (window.__ochre_video_modal_handlers) {
        if (window.__ochre_video_modal_handlers.esc) document.removeEventListener('keydown', window.__ochre_video_modal_handlers.esc);
        window.__ochre_video_modal_handlers = null;
      }
    } catch (e) {}
  }

  function buildVideoModal(videoData) {
    var root = document.getElementById('video-modal-root');
    if (!root) return null;
    removeExistingModal();

    var overlay = document.createElement('div');
    overlay.id = 'video-overlay';
    overlay.className = 'modal-overlay';

    var modal = document.createElement('div');
    modal.id = 'videoModal';
    modal.className = 'modal contact-form';

    var closeBtn = document.createElement('button');
    closeBtn.type = 'button';
    closeBtn.className = 'close modal-close icon-link';
    closeBtn.setAttribute('aria-label', 'Close');
    closeBtn.innerHTML = '&times;';
    closeBtn.addEventListener('click', function () { removeExistingModal(); });

    var content = document.createElement('div');
    content.className = 'modal-content';

    var videoContainer = document.createElement('div');
    videoContainer.id = 'modal-video-container';
    videoContainer.className = 'modal-video-container';

    // Create consistent media element
    var mediaEl = null;
    if (videoData.type === 'upload' || videoData.type === 'external') {
      mediaEl = document.createElement('video');
      mediaEl.setAttribute('controls', '');
      mediaEl.setAttribute('playsinline', '');
      mediaEl.src = videoData.url || videoData.embedUrl || '';
      mediaEl.className = 'modal-video';
    } else if (videoData.type === 'youtube' || videoData.type === 'embed') {
      // YouTube embed handling: extract ID and create iframe or fallback link
      var embedUrl = videoData.embedUrl || videoData.url || '';

      // Extract YouTube video ID from common URL formats or direct ID
      function getYouTubeID(url) {
        if (!url) return null;
        var patterns = [
          /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\?\/]+)/i,
          /^([a-zA-Z0-9_-]{11})$/
        ];
        for (var i = 0; i < patterns.length; i++) {
          var m = url.match(patterns[i]);
          if (m && m[1]) return m[1];
        }
        // attempt to extract src from iframe HTML
        var s = String(url).match(/src=["']([^"']+)["']/i);
        if (s && s[1]) {
          for (i = 0; i < patterns.length; i++) {
            m = s[1].match(patterns[i]);
            if (m && m[1]) return m[1];
          }
        }
        return null;
      }

      var videoID = getYouTubeID(embedUrl);
      if (videoID) {
        mediaEl = document.createElement('iframe');
        mediaEl.src = 'https://www.youtube-nocookie.com/embed/' + videoID + '?autoplay=1&rel=0';
        mediaEl.setAttribute('allowfullscreen', '');
        mediaEl.setAttribute('allow', 'autoplay; encrypted-media; picture-in-picture');
        mediaEl.style.width = '100%';
        mediaEl.style.height = '100%';
        mediaEl.className = 'modal-video';
      } else {
        // Fallback: provide a link to YouTube
        var a = document.createElement('a');
        a.href = embedUrl || '#';
        a.textContent = 'Watch on YouTube';
        a.target = '_blank';
        a.rel = 'noopener';
        a.style.color = '#fff';
        mediaEl = a;
      }
    } else {
      // fallback: show title only
      mediaEl = document.createElement('div');
      mediaEl.className = 'modal-video modal-video--fallback';
      mediaEl.textContent = 'Video unavailable';
    }

    // Wrap media in responsive ratio container
    var ratio = document.createElement('div');
    ratio.className = 'video-ratio';
    ratio.appendChild(mediaEl);
    videoContainer.appendChild(ratio);

    // Title element (inline styles for dynamic modal)
    var titleEl = document.createElement('h3');
    titleEl.id = 'modal-title';
    titleEl.className = 'modal-title';
    titleEl.textContent = videoData.title || 'Video';
    titleEl.style.marginTop = '1.5rem';
    titleEl.style.marginBottom = '0.5rem';
    titleEl.style.color = '#fff';

    // Description element (inline styles for dynamic modal)
    var descEl = document.createElement('div');
    descEl.id = 'modal-description';
    descEl.className = 'modal-description';
    descEl.innerHTML = videoData.description || '';
    descEl.style.marginTop = '0.5rem';
    descEl.style.color = '#ccc';
    descEl.style.lineHeight = '1.6';

    content.appendChild(videoContainer);
    content.appendChild(titleEl);
    content.appendChild(descEl);

    modal.appendChild(closeBtn);
    modal.appendChild(content);

    root.appendChild(overlay);
    root.appendChild(modal);

    function escHandler(e) { if (e.key === 'Escape') removeExistingModal(); }
    document.addEventListener('keydown', escHandler);
    window.__ochre_video_modal_handlers = { esc: escHandler };

    overlay.addEventListener('click', function () { removeExistingModal(); });

    return { destroy: removeExistingModal };
  }

  // Click handler for commercial cards — target `.commercial-card` elements
  document.querySelectorAll('.commercials-grid .commercial-card').forEach(function (el) {
    el.addEventListener('click', function (ev) {
      // element is a div, not an anchor
      var dataset = el.dataset || {};
      var videoData = {
        type: dataset.type || 'upload',
        url: dataset.url || '',
        embedUrl: dataset.embedUrl || dataset.embedurl || '',
        title: dataset.title || (el.querySelector('.collection-card-title') ? el.querySelector('.collection-card-title').textContent.trim() : ''),
        description: dataset.description || (el.querySelector('.full-desc') ? el.querySelector('.full-desc').innerHTML : (el.querySelector('.collection-card-excerpt') ? el.querySelector('.collection-card-excerpt').textContent : ''))
      };

      // If no dataset URL/embed available, try to discover iframe or video inside the card DOM
      if (!videoData.url && !videoData.embedUrl) {
        var foundIframe = el.querySelector('iframe');
        var foundVideo = el.querySelector('video source, video');
        if (foundIframe && foundIframe.src) {
          videoData.embedUrl = foundIframe.src;
          videoData.type = 'embed';
        } else if (foundVideo) {
          // handle <video><source src=...></video>
          var srcEl = el.querySelector('video source');
          if (srcEl && srcEl.src) {
            videoData.url = srcEl.src;
            videoData.type = 'upload';
          } else if (el.querySelector('video') && el.querySelector('video').currentSrc) {
            videoData.url = el.querySelector('video').currentSrc;
            videoData.type = 'upload';
          }
        }
      }
      buildVideoModal(videoData);
    });
  });

});

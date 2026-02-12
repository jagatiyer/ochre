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
        if (window.__ochre_video_modal_handlers.keynav) document.removeEventListener('keydown', window.__ochre_video_modal_handlers.keynav);
        window.__ochre_video_modal_handlers = null;
      }
    } catch (e) {}
  }
  // Build modal skeleton (only creates structure). Media/content will be loaded
  // via `loadIntoModal` so we can reuse the modal DOM and swap content.
  function buildVideoModalSkeleton() {
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

    // placeholder ratio container (media will be appended here)
    var ratio = document.createElement('div');
    ratio.className = 'video-ratio';
    videoContainer.appendChild(ratio);

    // Title and description placeholders
    var titleEl = document.createElement('h3');
    titleEl.id = 'modal-title';
    titleEl.className = 'modal-title';
    titleEl.style.marginTop = '1.5rem';
    titleEl.style.marginBottom = '0.5rem';
    titleEl.style.color = '#fff';

    var descEl = document.createElement('div');
    descEl.id = 'modal-description';
    descEl.className = 'modal-description';
    descEl.style.marginTop = '0.5rem';
    descEl.style.color = '#ccc';
    descEl.style.lineHeight = '1.6';

    // Prev/Next buttons (created but handlers attached later)
    var prevBtn = document.createElement('button');
    prevBtn.className = 'commercials-prev';
    prevBtn.type = 'button';
    prevBtn.setAttribute('aria-label', 'Previous');
    prevBtn.textContent = '‹';

    var nextBtn = document.createElement('button');
    nextBtn.className = 'commercials-next';
    nextBtn.type = 'button';
    nextBtn.setAttribute('aria-label', 'Next');
    nextBtn.textContent = '›';

    content.appendChild(videoContainer);
    content.appendChild(titleEl);
    content.appendChild(descEl);

    modal.appendChild(closeBtn);
    modal.appendChild(prevBtn);
    modal.appendChild(nextBtn);
    modal.appendChild(content);

    root.appendChild(overlay);
    root.appendChild(modal);

    overlay.addEventListener('click', function () { removeExistingModal(); });

    return {
      root: root,
      overlay: overlay,
      modal: modal,
      ratio: ratio,
      titleEl: titleEl,
      descEl: descEl,
      prevBtn: prevBtn,
      nextBtn: nextBtn,
      destroy: removeExistingModal
    };
  }

  // Load card data into an existing modal skeleton (replace media/title/desc)
  function loadIntoModal(cardEl, modalObj) {
    if (!cardEl || !modalObj) return;
    var dataset = cardEl.dataset || {};
    var videoData = {
      type: dataset.type || 'upload',
      url: dataset.url || '',
      embedUrl: dataset.embedUrl || dataset.embedurl || '',
      title: dataset.title || (cardEl.querySelector && (cardEl.querySelector('h3, h4') ? cardEl.querySelector('h3, h4').textContent.trim() : '')),
      description: dataset.description || ''
    };

    // If dataset empty, try to discover sources in DOM
    if (!videoData.url && !videoData.embedUrl) {
      var foundIframe = cardEl.querySelector('iframe');
      var foundVideo = cardEl.querySelector('video source, video');
      if (foundIframe && foundIframe.src) {
        videoData.embedUrl = foundIframe.src;
        videoData.type = 'embed';
      } else if (foundVideo) {
        var srcEl = cardEl.querySelector('video source');
        if (srcEl && srcEl.src) {
          videoData.url = srcEl.src;
          videoData.type = 'upload';
        } else if (cardEl.querySelector('video') && cardEl.querySelector('video').currentSrc) {
          videoData.url = cardEl.querySelector('video').currentSrc;
          videoData.type = 'upload';
        }
      }
    }

    // Clear existing media inside ratio
    while (modalObj.ratio.firstChild) modalObj.ratio.removeChild(modalObj.ratio.firstChild);

    // Create media element similar to original logic
    var mediaEl = null;
    if (videoData.type === 'upload' || videoData.type === 'external') {
      mediaEl = document.createElement('video');
      mediaEl.setAttribute('controls', '');
      mediaEl.setAttribute('playsinline', '');
      mediaEl.src = videoData.url || videoData.embedUrl || '';
      mediaEl.className = 'modal-video';
      try { mediaEl.play && mediaEl.play(); } catch (e) {}
    } else if (videoData.type === 'youtube' || videoData.type === 'embed') {
      var embedUrl = videoData.embedUrl || videoData.url || '';
      // fallback simple id extraction
      var videoID = null;
      var m = String(embedUrl).match(/(?:v=|\/embed\/|youtu\.be\/)([A-Za-z0-9_-]{11})/);
      if (m && m[1]) videoID = m[1];
      if (videoID) {
        mediaEl = document.createElement('iframe');
        mediaEl.src = 'https://www.youtube-nocookie.com/embed/' + videoID + '?autoplay=1&rel=0';
        mediaEl.setAttribute('allowfullscreen', '');
        mediaEl.setAttribute('allow', 'autoplay; encrypted-media; picture-in-picture');
        mediaEl.style.width = '100%';
        mediaEl.style.height = '100%';
        mediaEl.className = 'modal-video';
      } else {
        var a = document.createElement('a');
        a.href = embedUrl || '#';
        a.textContent = 'Watch on external site';
        a.target = '_blank';
        a.rel = 'noopener';
        a.style.color = '#fff';
        mediaEl = a;
      }
    } else {
      mediaEl = document.createElement('div');
      mediaEl.className = 'modal-video modal-video--fallback';
      mediaEl.textContent = 'Video unavailable';
    }

    modalObj.ratio.appendChild(mediaEl);
    modalObj.titleEl.textContent = videoData.title || 'Video';
    modalObj.descEl.innerHTML = videoData.description || '';
  }

  // Click handler for commercial cards — target `.commercial-card` elements
  // gather ordered cards for client-side navigation
  var cards = Array.from(document.querySelectorAll('.commercials-grid .commercial-card'));
  var currentIndex = -1;
  var modalObj = null;

  function openModalForIndex(idx) {
    if (idx < 0 || idx >= cards.length) return;
    currentIndex = (idx + cards.length) % cards.length;
    if (!modalObj) modalObj = buildVideoModalSkeleton();
    loadIntoModal(cards[currentIndex], modalObj);
    // attach nav handlers once
    attachModalHandlers(modalObj);
  }

  // attach click listeners on cards
  cards.forEach(function (el, i) {
    el.addEventListener('click', function (ev) {
      ev.stopPropagation();
      ev.preventDefault();
      openModalForIndex(i);
    });
  });

  // attach modal arrow and keyboard handlers
  function attachModalHandlers(modalObjRef) {
    if (!modalObjRef) return;
    // avoid double-binding
    if (modalObjRef._handlersAttached) return;

    function goPrev() {
      currentIndex = (currentIndex - 1 + cards.length) % cards.length;
      loadIntoModal(cards[currentIndex], modalObjRef);
    }
    function goNext() {
      currentIndex = (currentIndex + 1) % cards.length;
      loadIntoModal(cards[currentIndex], modalObjRef);
    }

    modalObjRef.prevBtn.addEventListener('click', function(e){
      e.stopPropagation();
      goPrev();
    });

    modalObjRef.nextBtn.addEventListener('click', function(e){
      e.stopPropagation();
      goNext();
    });

    function keyNav(e) {
      if (!document.getElementById('videoModal')) return;
      if (e.key === 'ArrowLeft') { goPrev(); }
      else if (e.key === 'ArrowRight') { goNext(); }
      else if (e.key === 'Escape') { removeExistingModal(); }
    }

    document.addEventListener('keydown', keyNav);
    // store handlers for cleanup
    window.__ochre_video_modal_handlers = window.__ochre_video_modal_handlers || {};
    window.__ochre_video_modal_handlers.keynav = keyNav;

    modalObjRef._handlersAttached = true;
  }

});

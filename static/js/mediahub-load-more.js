// Lazy-load next pages of All Press Coverage
(function(){
  function escapeHtml(str){
    if(!str) return '';
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  document.addEventListener('DOMContentLoaded', function(){
    var btn = document.getElementById('load-more-press');
    if(!btn) return;
    var page = parseInt(btn.getAttribute('data-page') || '1', 10);
    var url = btn.getAttribute('data-url');
    var PAGE_SIZE = parseInt(btn.getAttribute('data-page-size') || '10', 10);
    var loading = false;

    btn.addEventListener('click', function(){
      if(loading) return;
      loading = true;
      btn.disabled = true;
      var next = page + 1;
      var fetchUrl = url + '?page=' + next;
      btn.textContent = 'Loading...';

      fetch(fetchUrl, { method: 'GET', credentials: 'same-origin' })
        .then(function(resp){ if(!resp.ok) throw new Error('Network error'); return resp.json(); })
        .then(function(data){
          var container = document.querySelector('.press-list');
          if(!container){
            console.warn('press-list container not found');
          }
          data.articles.forEach(function(a){
            var item = document.createElement('div');
            item.className = 'press-list-item';
            var imgHtml = '';
            if(a.cover_image_url){
              imgHtml = '<div class="publication-logo-img"><img src="'+escapeHtml(a.cover_image_url)+'" alt="'+escapeHtml(a.title)+'"></div>';
            } else {
              imgHtml = '<i class="fa-regular fa-newspaper"></i>';
            }
            item.innerHTML = '<div>\n' +
              '  <div class="publication-logo">'+ imgHtml +'</div>\n' +
              '  <div class="item-meta">\n' +
              '    <span class="publication-name">'+ escapeHtml(a.publication_name) +'</span>\n' +
              '    <span class="separator">•</span>\n' +
              '    <span class="item-date">'+ escapeHtml(a.date) +'</span>\n' +
              '  </div>\n' +
              '</div>\n' +
              '<div class="item-content">\n' +
              '  <h3 class="item-title">'+ escapeHtml(a.title) +'</h3>\n' +
              '</div>\n' +
              '<div>\n' +
              '  <a href="/mediahub/press/'+ escapeHtml(a.slug) +'/" class="cn">READ ARTICLE <i class="fa-solid fa-arrow-up-right-from-square"></i></a>\n' +
              '</div>';
            container.appendChild(item);
          });

          // update page state
          page = next;
          btn.setAttribute('data-page', String(page));

          // Determine whether there are more items.
          var has_more = typeof data.has_more !== 'undefined' ? !!data.has_more : (data.articles.length >= PAGE_SIZE);

          loading = false;
          btn.disabled = false;
          if(has_more){
            btn.textContent = 'SEE MORE';
          } else {
            btn.textContent = 'No more entries...';
            btn.disabled = true;
          }
        })
        .catch(function(err){
          console.error(err);
          btn.textContent = 'Error';
          loading = false;
          btn.disabled = false;
        });
    });
  });
})();

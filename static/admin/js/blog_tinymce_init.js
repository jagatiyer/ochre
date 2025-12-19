document.addEventListener('DOMContentLoaded', function () {
  // Ensure TinyMCE script is available
  if (typeof window.tinymce === 'undefined') return;

  // Ensure the textarea is enabled before init
  var textarea = document.getElementById('id_content');
  if (textarea) {
    textarea.removeAttribute('disabled');
    textarea.readOnly = false;
  }

  tinymce.init({
    selector: '#id_content',
    readonly: false,
    plugins: 'lists link image code advlist autolink',
    toolbar: 'formatselect | bold italic underline | bullist numlist | blockquote | link | image | undo redo',
    menubar: false,
    statusbar: false,
    branding: false,
    setup: function (editor) {
      editor.on('init', function () {
        try {
          editor.setMode('design');
        } catch (e) {}
        var ta = document.getElementById('id_content');
        if (ta) {
          ta.removeAttribute('disabled');
          ta.readOnly = false;
        }
      });
    },
    images_upload_url: '/blog/tinymce/upload/',
    images_upload_handler: function (blobInfo, success, failure) {
      var xhr = new XMLHttpRequest();
      xhr.open('POST', '/blog/tinymce/upload/');
      xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
      function getCookie(name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length === 2) return parts.pop().split(';').shift();
      }
      var csrftoken = getCookie('csrftoken');
      if (csrftoken) xhr.setRequestHeader('X-CSRFToken', csrftoken);
      xhr.onload = function () {
        if (xhr.status !== 200) { failure('HTTP Error: ' + xhr.status); return; }
        var json = JSON.parse(xhr.responseText);
        if (!json || typeof json.location != 'string') { failure('Invalid JSON: ' + xhr.responseText); return; }
        success(json.location);
      };
      var formData = new FormData();
      formData.append('image', blobInfo.blob(), blobInfo.filename());
      xhr.send(formData);
    }
  });
});

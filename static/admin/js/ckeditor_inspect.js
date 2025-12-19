// Small inspector to log the available CKEditor plugins for the loaded build.
(function () {
  function inspect() {
    try {
      var Editor = window.ClassicEditor || (window.CKEditor && window.CKEditor.ClassicEditor);
      if (!Editor) {
        console.log('CKEditor inspector: ClassicEditor not found on window yet.');
        return;
      }
      if (Array.isArray(Editor.builtinPlugins)) {
        var names = Editor.builtinPlugins.map(function (p) { return p.pluginName; });
        console.log('CKEditor inspector: builtinPlugins ->', names);
      } else {
        console.log('CKEditor inspector: builtinPlugins not available on editor.');
      }
    } catch (e) {
      console.error('CKEditor inspector error', e);
    }
  }

  // Run after a short delay to allow scripts to load. If not present, try again.
  setTimeout(function attempt() {
    inspect();
    // try one more time later in case CKEditor initializes later
    setTimeout(inspect, 1000);
  }, 300);
})();

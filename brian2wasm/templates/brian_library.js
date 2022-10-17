mergeInto(LibraryManager.library, {
  brian_report_progress: function (elapsed, completed, start, duration) {
    console.log('In brian_report_progress')
    postMessage({
      type: 'progress',
      elapsed: elapsed, completed: completed, start: start, duration: duration
    });
  }
});

"use strict";

{
  const dataset = document.currentScript.dataset;
  const workerScriptPath = dataset.workerScriptPath;
  const eventsPath = dataset.eventsPath;

  if (!window.SharedWorker) {
    console.debug("😭 django-browser-reload cannot work in this browser.");
  } else {
    const worker = new SharedWorker(workerScriptPath);

    worker.port.addEventListener("message", (event) => {
      if (event.data === "Reload") {
        location.reload();
      }
    });

    worker.port.postMessage({
      type: "initialize",
      eventsPath: eventsPath,
    });

    worker.port.start();
  }
}

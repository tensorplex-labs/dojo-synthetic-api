function logErrorToServer(errorData) {
  // sends errors to endpoint defined in server.js
  fetch("/log-error", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(errorData),
  }).catch(console.error);
}

window.onunhandledrejection = function (event) {
  const errorData = {
    type: "unhandledRejection",
    reason: event.reason.toString(),
    stack: event.reason.stack,
  };
  logErrorToServer(errorData);
  console.error("Unhandled Rejection (window): " + JSON.stringify(event));
};

window.addEventListener("error", function (event) {
  const errorData = {
    type: event.error ? event.error.name : "Error", // Default to "Error" if event.error is undefined
    message: event.error ? event.error.message : event.message,
    source: event.filename,
    lineno: event.lineno,
    colno: event.colno,
    error: event.error ? event.error.toString() : event.message,
    stack: event.error ? event.error.stack : null,
  };
  logErrorToServer(errorData);
  console.error(`Uncaught ${errorData.type}: ${errorData.message}`);
});

const express = require("express");
const fs = require("fs");
const winston = require("winston");
// Define the log file path to be in the /untrusted folder
const logFilePath = "/untrusted/app.log";

// Create a logger
const logger = winston.createLogger({
  level: "debug",
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.printf(({ timestamp, level, message }) => {
      return `${timestamp} [${level.toUpperCase()}]: ${message}`;
    })
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({
      filename: logFilePath,
      handleExceptions: true,
      maxsize: 5242880, // 5MB
      maxFiles: 5,
    }),
  ],
});

// Test file writing and create if doesn't exist
fs.access(logFilePath, fs.constants.F_OK | fs.constants.W_OK, (err) => {
  if (err) {
    if (err.code === "ENOENT") {
      // File doesn't exist, create it
      fs.writeFile(logFilePath, "", (createErr) => {
        if (createErr) {
          console.error(`Cannot create log file: ${createErr.message}`);
        }
      });
    } else {
      console.error(`Cannot access log file: ${err.message}`);
    }
  }
});

const app = express();
const port = 3000;

app.use(express.static("/untrusted"));
app.use(express.json());

// Define the client-side error logging script
// TODO fix uncaught type errors on client siode
const errorLoggingScript = `
<script>
function logErrorToServer(errorData) {
  fetch('/log-error', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(errorData),
  }).catch(console.error);
}

window.onunhandledrejection = function (event) {
  const errorData = {
    type: 'unhandledRejection',
    reason: event.reason.toString(),
    stack: event.reason.stack
  };
  logErrorToServer(errorData);
  console.error("Unhandled Rejection (window): " + JSON.stringify(event));
};

window.addEventListener('error', function(event) {
  const errorData = {
    type: 'TypeError',
    message: event.error.message,
    stack: event.error.stack
  };
  logErrorToServer(errorData);
  console.error("Uncaught TypeError: " + event.error.message);
});
</script>
`;

app.get("/", (req, res) => {
  logger.info("Request received");
  try {
    let html = fs.readFileSync("/untrusted/index.html", "utf8");
    if (html.includes(errorLoggingScript)) {
      logger.info("Error logging script successfully added");
    } else {
      logger.info("Error logging script not found in HTML");
    }

    // Set headers to prevent caching
    res.setHeader(
      "Cache-Control",
      "no-store, no-cache, must-revalidate, proxy-revalidate"
    );
    res.setHeader("Pragma", "no-cache");
    res.setHeader("Expires", "0");
    res.setHeader("Surrogate-Control", "no-store");
    res.setHeader("Clear-Site-Data", '"cache"');

    res.send(html);
  } catch (error) {
    console.error("Server error:", error);
    res.status(500).send("An error occurred");
  }
});

// Add new endpoint for client-side error logging
app.post("/log-error", (req, res) => {
  logger.error(`Client Error occurred: ${JSON.stringify(req.body, null, 2)}`);
  res.sendStatus(200);
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});

// Global error handler
process.on("uncaughtException", (error) => {
  logger.error("Uncaught Exception:", error);
});

process.on("unhandledRejection", (reason, promise) => {
  logger.error("Unhandled Rejection at:", promise, "reason:", reason);
});

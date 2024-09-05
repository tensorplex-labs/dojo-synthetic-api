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
        } else {
          logger.info("Log file created and is writable");
        }
      });
    } else {
      console.error(`Cannot access log file: ${err.message}`);
    }
  } else {
    logger.info("Log file exists and is writable");
  }
});

const app = express();
const port = 3000;

app.use(express.static("/untrusted"));
app.use(express.json());

// Define the client-side error logging script
// Define the client-side error logging script
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

window.onerror = function (message, source, lineno, colno, error) {
  const errorData = { type: 'error', message, source, lineno, colno, error: error.toString() };
  logErrorToServer(errorData);
  console.error(\`Client error: \${error}, message: \${message} at \${source} line: \${lineno} col:\${colno}\`);
};

window.onunhandledrejection = function (event) {
  const errorData = { type: 'unhandledRejection', reason: event.reason.toString() };
  logErrorToServer(errorData);
  console.error("Unhandled Rejection (window): " + JSON.stringify(event));
};
</script>
`;

app.get("/", (req, res) => {
  logger.info("Request received");
  try {
    let html = fs.readFileSync("/untrusted/index.html", "utf8");
    logger.info("Original HTML length:", html.length);
    // html = html.replace("</head>", `${errorLoggingScript}</head>`);
    html = html.replace("</body>", `${errorLoggingScript}</body>`);
    logger.info("Modified HTML length:", html.length);
    logger.info("Modified HTML:", html);
    if (html.includes(errorLoggingScript)) {
      logger.info("Error logging script successfully added");
    } else {
      logger.info("Error logging script not found in HTML");
    }
    res.send(html);
  } catch (error) {
    console.error("Server error:", error);
    res.status(500).send("An error occurred");
  }
});

// Add new endpoint for client-side error logging
app.post("/log-error", (req, res) => {
  const errorData = req.body;
  if (errorData.type === "error") {
    logger.error(
      `Client Error: ${errorData.message} at ${errorData.source} line: ${errorData.lineno} col: ${errorData.colno}\nError: ${errorData.error}`
    );
  } else if (errorData.type === "unhandledRejection") {
    logger.error(`Client Unhandled Rejection: ${errorData.reason}`);
  }
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

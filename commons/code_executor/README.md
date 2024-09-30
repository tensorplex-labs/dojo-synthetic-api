# code executor

# aim

to catch errors

## how it works

the following is how `get_feedback` is supposed to work, which is the main function to call to get feedback on any piece of code.

1. firstly ensures that a docker image that runs a nodejs server is build.
2. creates a temporary folder inside of `commons/code_executor/sandbox-workspace/`, called `run\_<run_uuid>`
3. injects error logging javascript code as inline javascript into a HTML file, and writes it into `index.html` to be served by the nodejs server
4. searches for a free port on the host machine in the range 3000-3999
5. runs a docker container for the nodejs server with an error logging endpoint, and serves an `index.html` on the port <port_no>
6. uses headless puppeteer to visit the page at `http://localhost:<port_no>` to trigger rendering of the page
7. on errors like SyntaxError, TypeError, etc. these get written into the app.log when the client-side calls the error logging endpoint on the server-side
8. reads the contents of `app.log` (in the same folder as index.html) and returns it to the caller

## types of errors caught so far

- Syntax Error
- Type Error
- Reference Error

## todo

- [ ] errors that occur during interaction of different components

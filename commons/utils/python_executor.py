import sys
import time

sys.path.append("./")
import os
import re
import json
import base64
from typing import Optional, List, DefaultDict, Any, cast
from collections import defaultdict
from dotenv import load_dotenv
import httpx
import pandas as pd
from loguru import logger
from e2b_code_interpreter import CodeInterpreter
from e2b_code_interpreter.models import Result
from e2b.sandbox.filesystem_watcher import FilesystemEvent
from commons.utils.utils import get_packages, ExecutionError

load_dotenv()

PLOTLY_TEMPLATE = """
<!DOCTYPE html>
<html>

<head>
    <title>Python Executor</title>
    <script src="https://cdn.plot.ly/plotly-2.32.0.min.js" charset="utf-8"></script>
</head>

<body>
    <div id="tester" style="width:600px;height:250px;"></div>
    <script>
        var plotData = {plotData};

        Plotly.newPlot('tester', plotData.data, plotData.layout);
    </script>
</body>

</html>
"""

IMG_TEMPLATE = """
<img src="data:image/png;base64, {img}" />
"""

SCRIPT_TEMPLATE = """
<script>
    {script}
</script>
"""

BASE_TEMPLATE = """
<!DOCTYPE html>
<html>

<head>
    <title>Python Executor</title>
</head>

<body>
    {content}
</body>

</html>
"""

def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper

class PythonExecutor:
    def __init__(self, code: Optional[str] = None , file : Optional[str] = None, debug : bool = False):
        if code is None and file is None:
            raise ValueError("Either code or file should be provided")
        
        if code is not None and file is not None:
            raise ValueError("Only one of code or file should be provided")
        
        if code is not None:
            self.code = code
        elif file is not None:
            with open(file, "r") as f:
                self.code = f.read()
                
        self.created_files : DefaultDict[str, Any] = defaultdict(list)
        self.debug = debug
        self.preprocess_code()
        # print("Code preprocessed")
        # print(self.code)
        
    def preprocess_code(self):     
        self.code = self.replace_mpld3_show(self.code)
        
    def initialize_sandbox(self):
        watch_tmp = False
        packages = " ".join(get_packages(self.code))
        if "bokeh" in packages:
            watch_tmp = True
            
        sandbox = CodeInterpreter(cwd = "/home/user")
        kernel_id = sandbox.notebook.create_kernel(cwd = "/home/user")
        logger.debug(f"Installing packages {packages}")
        sandbox.notebook.exec_cell(f"!pip install {packages}", kernel_id = kernel_id)
        self.sandbox = sandbox
        self.kernel_id = kernel_id
        self.start_watcher(watch_tmp=watch_tmp)

    def execute(self):
        self.initialize_sandbox()        
        ports = self.get_running_ports()
        execution = self.sandbox.notebook.exec_cell(self.code, on_stderr= print, on_stdout= print)
        if execution.error:
            raise ExecutionError(execution.error.traceback, self.code)
        
        results = execution.results
        final_ports = self.get_running_ports()
        if z := final_ports - ports:
            port = z.pop()
            url = "https://" + self.sandbox.get_hostname(port) 
            return self.get_webpage(url)
        
        return self.handle_responses(results)
    
    def close_sandbox(self):
        print("Closing sandbox")
        self.sandbox.close()
        
    def get_running_ports(self) -> set[int]:
        self.install_lsof()
        initial_ports = self.sandbox.process.start_and_wait(cmd = "lsof -i -P -n | grep LISTEN | awk '{print $9}' | sed 's/.*://'")
        all_ports = initial_ports.stdout.split("\n")
        return set([int(port) for port in all_ports if port != "" and len(port) < 5 and port != "8888"])
        
    @staticmethod
    def replace_mpld3_show(code: str):
        pattern = r'mpld3\.show\((\w*)\)'
        replacement = r'mpld3.display(\1)'
        return re.sub(pattern, replacement, code)
    
    @staticmethod
    def _list_dir(sandbox : CodeInterpreter, dir : str):
        content = sandbox.filesystem.list(dir)  
        for item in content:
            print(f"Is '{item.name}' directory?", item.is_dir)
        print("------------------------------------")
        
    @run_once
    def install_lsof(self):
        logger.debug("Installing lsof")
        self.sandbox.process.start_and_wait(cmd = "sudo apt-get install lsof")
        
    def get_webpage(self, url : str):
        response = httpx.get(url)
        if response.status_code == 200:
            logger.info(f"Returning webpage from {url}")
            return response.text
        
        return BASE_TEMPLATE.format(content = "")
        
    def start_watcher(self, dir : str = "/home/user", watch_tmp : bool = False):
        def download_file(event : FilesystemEvent):
            logger.info(f"Operation {event.operation} {event.path}")
            if event.operation == "Write":
                file_path = event.path
                file_name = os.path.basename(file_path)
                if file_name.endswith(".html"):
                    bytes_file = self.sandbox.download_file(file_path, timeout=None)
                    self.created_files[file_name] = bytes_file.decode("utf-8")
                
                if file_name.endswith(".png"):
                    bytes_file = self.sandbox.download_file(file_path, timeout=None)
                    img_tag = IMG_TEMPLATE.format(img=base64.b64encode(bytes_file).decode("utf-8"))
                    self.created_files[file_name] = BASE_TEMPLATE.format(content = img_tag)
                    
        if watch_tmp:
            tmp_watcher = self.sandbox.filesystem.watch_dir("/tmp")
            tmp_watcher.add_event_listener(lambda event: download_file(event))
            logger.debug("Watching /tmp directory")
            tmp_watcher.start()
        
        watcher = self.sandbox.filesystem.watch_dir(dir)  
        watcher.add_event_listener(lambda event: download_file(event))  
        watcher.start()
        
    def handle_responses(self, results : List[Result])-> str:  
        if len(self.created_files) != 0:
            # print(self.created_files.keys())
            keys = list(self.created_files.keys())
            logger.info(f"Returning file {keys[0]}")
            return self.created_files[keys[0]]
        else:
            raise ExecutionError("Visualisation must be saved to an external file", self.code)
        
        ## Uncomment this block to handle kernel outputs
        # return self.handle_output(results)
    
    def handle_output(self, results : List[Result]):
        datatypes = defaultdict(list)
        for result in results:
            df = pd.json_normalize(result.raw, max_level = 0)
            result_dict = df.to_dict(orient='records')[0]
            for key, value in result_dict.items():
                datatypes[key].append(value)
                
        if self.debug:
            with open("output.json", "w") as f:
                dump = [vars(result) for result in results]
                json.dump(dump, f)     
            with open("output_formatted.json", "w") as f:
                json.dump(datatypes, f)
                
        if "application/vnd.plotly.v1+json" in datatypes:
            plot_data = datatypes["application/vnd.plotly.v1+json"][0]
            dumps = json.dumps(plot_data)
            return PLOTLY_TEMPLATE.format(plotData = dumps)

        content_parts = []
        if "text/html" in datatypes:
            content_parts.extend(datatypes["text/html"])
        if "image/png" in datatypes:
            content_parts.append(IMG_TEMPLATE.format(img=datatypes["image/png"].pop()))
        if "application/javascript" in datatypes:
            content_parts.append(SCRIPT_TEMPLATE.format(script="\n".join(datatypes["application/javascript"])))
        content = "\n".join(content_parts)
        logger.info(f"Returning content from kernel output")
        return BASE_TEMPLATE.format(content = content)
    
    def main(self):
        MAX_RETRIES = 3
        RETRY_DELAY = 3  # seconds

        for retry_count in range(MAX_RETRIES):
            try:
                output = self.execute()
                return output  # If execution succeeds, break out of the retry loop
            except Exception as e:
                self.close_sandbox()
                
                if retry_count < MAX_RETRIES - 1:
                    logger.warning(f"Execution failed. Retrying in {RETRY_DELAY} seconds... (Attempt {retry_count + 1}/{MAX_RETRIES})")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"Execution failed after {MAX_RETRIES} attempts. Raising exception.")
                    raise e
                
        self.close_sandbox()
    
if __name__ == "__main__":
    test_code = """
import plotly.express as px
fig = px.scatter(x=range(10), y=range(10))
fig.show()"""
    for _ in range(5):
        executor = PythonExecutor(code = test_code, debug = True)
        try:
            output = executor.main()
        except ExecutionError as e:
            print(e.err)
            del executor
            continue
        del executor
        if output is not None:
            with open("output.html", "w") as f:
                f.write(output)
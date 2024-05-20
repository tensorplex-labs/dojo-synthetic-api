import sys

sys.path.append("./")
import os
import json
from typing import Optional, List, DefaultDict, Any, cast
from collections import defaultdict
from dotenv import load_dotenv
import httpx
import pandas as pd
from e2b_code_interpreter import CodeInterpreter
from e2b_code_interpreter.models import Result
from e2b.sandbox.filesystem_watcher import FilesystemEvent
from commons.utils.utils import get_packages

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

class PythonExecutor:
    def __init__(self, code: Optional[str] = None , file : Optional[str] = None):
        if code is None and file is None:
            raise ValueError("Either code or file should be provided")
        
        if code is not None and file is not None:
            raise ValueError("Only one of code or file should be provided")
        
        if code is not None:
            self.code = code
        elif file is not None:
            with open(file, "r") as f:
                self.code = f.read()
                
        self.created_files : DefaultDict[str, List] = defaultdict(list)

    def execute(self):
        packages = " ".join(get_packages(self.code))
        with CodeInterpreter(cwd = "/home") as sandbox:
            sandbox.notebook.exec_cell(f"!pip install {packages}")
            results = sandbox.notebook.exec_cell(self.code).results
            print(self.created_files.keys())
            url = "https://" + sandbox.get_hostname(port = 5006)  
            # self.get_webpage(url)
            
            content = sandbox.filesystem.list("/")  
            for item in content:
                print(f"Is '{item.name}' directory?", item.is_dir)
            print("-------------------")
            
            content = sandbox.filesystem.list("/home")  
            for item in content:
                print(f"Is '{item.name}' directory?", item.is_dir)
            print("-------------------")
            content = sandbox.filesystem.list("/home/user")  
            for item in content:
                print(f"Is '{item.name}' directory?", item.is_dir)
    
            return self.handle_responses(results)
        
    def get_webpage(self, url : str):
        response = httpx.get(url)
        print(response.status_code)
        with open("test_response.json", "w") as f:
            json.dump(response.json(), f)
        
    def start_watcher(self, sandbox : CodeInterpreter, dir : str = "/home"):
        watcher = sandbox.filesystem.watch_dir(dir)  
        def download_file(event : FilesystemEvent):
            if event.operation == "Create":
                file_path = event.path
                file_name = os.path.basename(file_path)
                self.created_files[file_name].append(sandbox.filesystem.read(file_path))
        
        watcher.add_event_listener(lambda event: download_file(event))  
        watcher.start()  
        
    def handle_responses(self, results : List[Result])-> str | None:
        datatypes = defaultdict(list)
        for result in results:
            df = pd.json_normalize(result.raw, max_level = 0)
            result_dict = df.to_dict(orient='records')[0]
            for key, value in result_dict.items():
                datatypes[key].append(value)
            
        if "application/vnd.plotly.v1+json" in datatypes:
            plot_data = datatypes["application/vnd.plotly.v1+json"][0]
            dumps = json.dumps(plot_data)
            return PLOTLY_TEMPLATE.format(plotData = dumps)
        elif "text/html" in datatypes:
            return BASE_TEMPLATE.format(content = datatypes["text/html"].pop())
        elif "image/png" in datatypes:
            img_string = IMG_TEMPLATE.format(img = datatypes["image/png"].pop())
            return BASE_TEMPLATE.format(content = img_string)
    
if __name__ == "__main__":
    output = PythonExecutor(file = "plot_test.py").execute()
    # with open("output.json", "w") as f:
    #     json.dump(output, f)
    if output is not None:
        with open("output.html", "w") as f:
            f.write(output)
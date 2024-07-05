import sys

sys.path.append("./")
from commons.utils.python_executor import PythonExecutor


def test_code_executor():
    test_code = """
import plotly.express as px
df = px.data.iris()
df["e"] = df["sepal_width"]/100
fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species", error_x="e", error_y="e")
fig.write_html("test.html")
    """
    executor = PythonExecutor(code=test_code)
    executor.main()

    assert "test.html" in executor.created_files.keys()

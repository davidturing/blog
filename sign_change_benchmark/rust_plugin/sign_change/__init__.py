import polars as pl
import pathlib
from polars.plugins import register_plugin_function

def compute_sign_change(expr: pl.Expr) -> pl.Expr:
    lib = str(pathlib.Path(__file__).parent / "sign_change.so")
    return register_plugin_function(
        plugin_path=lib,
        function_name="compute_sign_change",
        is_elementwise=False,
    )

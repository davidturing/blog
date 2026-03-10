use numpy::ndarray::Array1;
use numpy::{IntoPyArray, PyArray1, PyReadonlyArray1};
use pyo3::prelude::*;

#[pyfunction]
fn symbol_switch_cumsum<'py>(
    py: Python<'py>,
    x: PyReadonlyArray1<'py, f64>,
) -> Bound<'py, PyArray1<i64>> {
    let x = x.as_array();
    let mut result = Array1::<i64>::zeros(x.len());
    
    if x.len() > 0 {
        let mut current_group = 0;
        for i in 1..x.len() {
            let prev_sign = x[i-1] >= 0.0;
            let curr_sign = x[i] >= 0.0;
            
            if prev_sign != curr_sign {
                current_group += 1;
            }
            result[i] = current_group;
        }
    }
    
    result.into_pyarray_bound(py)
}

#[pymodule]
fn symbol_switch_rust_plugin(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(symbol_switch_cumsum, m)?)?;
    Ok(())
}
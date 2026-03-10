use polars::prelude::*;
use pyo3::prelude::*;
use pyo3_polars::derive::polars_expr;

#[polars_expr(output_type=Int64)]
fn compute_sign_change(inputs: &[Series]) -> PolarsResult<Series> {
    let s = &inputs[0];
    let ca = s.f64()?;
    
    let mut group_id = 0i64;
    let mut last_sign: Option<bool> = None;
    
    let out: Int64Chunked = ca
        .into_iter()
        .map(|opt_val| {
            if let Some(val) = opt_val {
                let curr_sign = val >= 0.0;
                match last_sign {
                    Some(ls) => {
                        if ls != curr_sign {
                            group_id += 1;
                        }
                    }
                    None => {}
                }
                last_sign = Some(curr_sign);
                Some(group_id)
            } else {
                None 
            }
        })
        .collect();
        
    Ok(out.into_series())
}

#[pymodule]
fn sign_change(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}

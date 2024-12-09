# pairs_simulation
This is simulation for simple pairs trading

## How to Download Data

1. **Run `init_data.py`**  
   To download the data, execute the `init_data.py` script. This script automatically fetches data for the specified cryptocurrency trading pairs (BTCUSDT, ETHUSDT, SOLUSDT) and saves it in the `data/` folder.

   ### Usage:
   ```bash
   python init_data.py

## Simulation and Visualization

1. **Run the `pairs_simulation.ipynb` Notebook**  
   Navigate to the `pairs/` folder and open the `pairs_simulation.ipynb` notebook. Execute the cells step-by-step.

2. **Run the Visualization Function**  
   Inside the notebook, use the following function to visualize data:
   ```python
   visualize_all_periods(coin1, coin2, tf, window_size)

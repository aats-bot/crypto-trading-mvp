# tools/which_indicators.py
import inspect
import importlib

mod = importlib.import_module("src.indicators")
print("src.indicators path:", getattr(mod, "__file__", "<package>"))

from src.indicators import EMAIndicator, HeikinAshiIndicator, BaseIndicator
print("EMAIndicator from:", inspect.getsourcefile(EMAIndicator))
print("HeikinAshiIndicator from:", inspect.getsourcefile(HeikinAshiIndicator))
print("BaseIndicator from:", inspect.getsourcefile(BaseIndicator))

import inspect as _ins
print("EMA __init__ sig:", _ins.signature(EMAIndicator.__init__))
print("HA  __init__ sig:", _ins.signature(HeikinAshiIndicator.__init__))

# import matplotlib.pyplot as plt
# import matplotlib.dates  as mdates

# from ._CTD import read_ctd, quick_plot_ctd
# from ._LISST import read_lisst
# from ._ADCP import ADCP, quick_plot_profile
# from ._ADV import clean, quick_plot_adv, merge_masks


# __all__ = ['quick_plot_timeseries',     # from __init__.py
#            'read_ctd','quick_plot_ctd', # from _CTD.py
#            'read_lisst',                # from _LISST.py
#            'ADCP','quick_plot_profile', # from _ADCP.py
#            'clean','quick_plot_adv','merge_masks', # from _ADV.py
#            'dotdict']

from . import plot
from . import config
from . import news
from . import fx

__all__ = ['plot', 'config', 'news']
"""botplotlib version: 1 function call. Same result."""

import botplotlib as blt

data = {
    "trial": [1, 2, 3, 4, 5, 6, 7, 8],
    "cm": [2.3, 4.1, 3.5, 6.2, 5.8, 7.1, 8.3, 7.9],
}

fig = blt.scatter(data, x="trial", y="cm", title="Experiment Results")
fig.save_svg("experiment.svg")

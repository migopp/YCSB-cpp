# scripts

Here are scripts to automate the process of data collection.

To run a full data collection (as we used to gather data for the report):

```shell
just all
```

Or, using the raw python scripts:

```shell
# To collect data.
uv run benchmark.py [options]

# To summarize data.
uv run collect_stats.py

# To create graphs.
uv run graph.py
```

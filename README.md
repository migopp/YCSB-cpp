# YCSB-cpp

> kvstore fork super deluxe edition.

Yahoo! Cloud Serving Benchmark ([YCSB](https://github.com/brianfrankcooper/YCSB/wiki)) written in C++.

## Building

```shell
just build
```

## Running

From the project directory, after building:

``` shell
./ycsb -db [map name] -load -run -P [path to workload file]
```

For example, to run `ojdkchm_oa_db` on `workloads/workloada`:

``` shell
./ycsb -db ojdkchm_oa_db -load -run -P workloads/workloada
```

## Benchmarking

Experimental benchmarking scripts are available for convenience.
Check `scripts/README.md`.

To run a full benchmark:

``` shell
# (make sure to build first)
just build

# Then run it.
just bench
```

## Configuration

For detailed information about all available configuration properties, see [PROPERTIES.md](PROPERTIES.md).

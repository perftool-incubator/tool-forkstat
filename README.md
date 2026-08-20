# tool-forkstat
[![CI Actions Status](https://github.com/perftool-incubator/tool-forkstat/workflows/crucible-ci/badge.svg)](https://github.com/perftool-incubator/tool-forkstat/actions)

Monitors process fork(), exec(), exit(), and clone() activity during benchmark execution for the [crucible](https://github.com/perftool-incubator/crucible) performance testing framework, using the upstream [forkstat](https://github.com/ColinIanKing/forkstat) utility.

## Configuration

The start script accepts one parameter:
- `--events <list>` — Comma-separated event types to monitor (default: `all`)

## Integration

Forkstat runs as a profiler tool on endpoint nodes. It is allowed on master and worker collector roles but blocked on client and server roles. The post-processor (`forkstat-post-process`) converts raw forkstat output into crucible metrics.

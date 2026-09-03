#!/usr/bin/env python3
# -*- mode: python; indent-tabs-mode: nil; python-indent-level: 4 -*-
# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python

import sys
import os
import lzma
import re
import math
from datetime import datetime, timedelta
from pathlib import Path

TOOLBOX_HOME = os.environ.get('TOOLBOX_HOME')
if TOOLBOX_HOME is None:
    print("This script requires libraries that are provided by the toolbox project.")
    print("Toolbox can be acquired from https://github.com/perftool-incubator/toolbox and")
    print("then use 'export TOOLBOX_HOME=/path/to/toolbox' so that it can be located.")
    exit(1)
else:
    p = Path(TOOLBOX_HOME) / 'python'
    if not p.exists() or not p.is_dir():
        print("ERROR: <TOOLBOX_HOME>/python ('%s') does not exist!" % (p))
        exit(2)
    sys.path.append(str(p))
from toolbox.cdm_metrics import CDMMetrics

event_types = ('fork', 'exec', 'exit', 'clone')
event_pattern = re.compile(r'^(\d{2}:\d{2}:\d{2})\s+(' + '|'.join(event_types) + r')\s+')

def emit_samples(metrics, file_id, end_ts, counts):
    for event_type, count in counts.items():
        desc = {'source': 'forkstat', 'type': event_type, 'class': 'throughput'}
        sample = {'end': end_ts, 'value': count}
        metrics.log_sample(file_id, desc, {}, sample)

def main():
    print('forkstat-post-process')
    metrics = CDMMetrics()

    date_file = 'forkstat-date.txt'
    if not os.path.exists(date_file):
        print("ERROR: %s not found, cannot determine date for timestamps" % date_file)
        return 1

    with open(date_file, 'r') as f:
        date_str = f.read().strip()

    data_file = 'forkstat-stderrout.txt.xz'
    if not os.path.exists(data_file):
        print("ERROR: %s not found" % data_file)
        return 1

    file_id = '0'
    prev_hour = None
    day_offset = 0
    current_ts = None
    counts = {}

    with lzma.open(data_file, 'rt', errors='replace') as fh:
        for line in fh:
            match = event_pattern.match(line)
            if not match:
                continue

            time_str = match.group(1)
            event_type = match.group(2)

            cur_hour = int(time_str[:2])
            if prev_hour is not None and cur_hour < prev_hour:
                day_offset += 1
            prev_hour = cur_hour

            dt_str = "%s %s" % (date_str, time_str)
            dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
            if day_offset > 0:
                dt += timedelta(days=day_offset)
            end_ts = int(math.floor(dt.timestamp() * 1000))

            if current_ts is not None and end_ts != current_ts:
                emit_samples(metrics, file_id, current_ts, counts)
                counts = {}

            current_ts = end_ts
            counts[event_type] = counts.get(event_type, 0) + 1

    if current_ts is not None and counts:
        emit_samples(metrics, file_id, current_ts, counts)

    metrics.finish_samples()
    return 0

if __name__ == "__main__":
    exit(main())

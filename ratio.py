#!/usr/bin/env python
"""
Silly script to estimate recent LBRY ratio from logfiles
"""
import datetime
import matplotlib.pyplot as plt
import numpy as np

# This should work on Linux. On other OSs you can try
# just setting the directory string yourself.
# You might need escape characters. E.g. on windows
# it could be something like
# directory = "C:/Program\ Files/..."
from os.path import expanduser
home = expanduser("~")
directory = home + "/.local/share/lbry/lbrynet"

# Remove trailing slash if one was given
if directory[-1] == "/":
    directory = directory[0:-1]

# Filename endings
suffices = [""] + ["." + str(i) for i in range(10)]

# Blob counts
up = 0
down = 0

# Blob upload and download times
up_times = []
down_times = []

# Flag that becomes true ones a file has been successfully opened
success = False
for suffix in suffices:
    filename = directory + "/lbrynet.log" + suffix

    try:
        f = open(filename)
        lines = f.readlines()
        for line in lines:
            if "lbry.blob_exchange.server:" and "sent" in line:
                up += 1
                parts = line.split(" ")
                isoformat = (parts[0] + " " + parts[1]).replace(",", ".")
                up_times.append(datetime.datetime.fromisoformat(isoformat))
            if "lbry.blob_exchange.client:" and "downloaded" in line:
                down += 1
                parts = line.split(" ")
                isoformat = (parts[0] + " " + parts[1]).replace(",", ".")
                down_times.append(datetime.datetime.fromisoformat(isoformat))
        f.close()

        success = True
    except:
        pass

print("Success = {success}.".format(success=success))
if success:
    print("Downloaded {down} blobs.".format(down=down))
    print("Uploaded {up} blobs.".format(up=up))
    print("Ratio = {ratio}.".format(ratio=float(up)/down))

    # Convert to unix epochs
    import time
    now = time.time()
    up_times = np.array([t.timestamp() - now for t in up_times])/86400.0
    down_times = np.array([t.timestamp() - now for t in down_times])/86400.0
    t_min = np.min([np.min(up_times), np.min(down_times)])
    bins = [0.0]
    while bins[-1] > t_min:
        bins.append(bins[-1] - 1/24)
    bins = bins[::-1]

    plt.hist(down_times, bins=bins, alpha=0.5, label="Downloaded")
    plt.hist(up_times,   bins=bins, alpha=0.5, label="Uploaded")
    plt.legend()
    plt.xlabel("Time (days)")
    plt.ylabel("Blobs per hour")
    plt.show()



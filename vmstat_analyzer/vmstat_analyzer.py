# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.3'
#       jupytext_version: 0.8.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
#   language_info:
#     codemirror_mode:
#       name: ipython
#       version: 3
#     file_extension: .py
#     mimetype: text/x-python
#     name: python
#     nbconvert_exporter: python
#     pygments_lexer: ipython3
#     version: 3.7.1
# ---

# +
# %matplotlib inline

from datetime import datetime
import os
import sys

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

plt.style.use("ggplot")

plt.rcParams["font.size"]= 20
plt.rcParams["xtick.labelsize"]=20
plt.rcParams["ytick.labelsize"]=20
plt.rcParams["figure.figsize"]=(20,15)
# -

INT_VALUE   = dict(type="uint64",  regex=r"\d+?")
FLOAT_VALUE = dict(type="float64", regex=r"\d+?\.\d+?")

VMSTAT_COLUMNS = dict([
    ("proc", dict([
        ("run_queue", INT_VALUE),
        ("blocking",  INT_VALUE),
    ])),
    ("memory", dict([
        ("swapped",   INT_VALUE),
        ("free",      INT_VALUE),
        ("buffered",  INT_VALUE),
        ("cached",    INT_VALUE),
    ])),
    ("swap", dict([
        ("swap_in",   INT_VALUE),
        ("swap_out",  INT_VALUE),
    ])),
    ("io", dict([
        ("block_in",  INT_VALUE),
        ("block_out", INT_VALUE),
    ])),
    ("system", dict([
        ("interrupt", INT_VALUE),
        ("context_switch", INT_VALUE),
    ])),
    ("cpu", dict([
        ("user",      INT_VALUE),
        ("system",    INT_VALUE),
        ("idle",      INT_VALUE),
        ("io_wait",   INT_VALUE),
        ("steal",     INT_VALUE),
    ]))
])

def extract_pattern(category, column):
    return f"(?P<{column}>{VMSTAT_COLUMNS[category][column]['regex']})"

def convert_type(df):
    for columns in VMSTAT_COLUMNS.values():
        for key, value_type in columns.items():
            df[key] = df[key].astype(value_type['type'])
    
    df['timestamp'] = df['timestamp'].apply(lambda d: datetime.strptime(d, "%Y-%m-%d %H:%M:%S"))

def ceiling(data_series):
    str_val = str(int(max(data_series)))
    digits  = len(str_val)
    
    # 1桁なら10
    if digits == 1:
        return 10

    # 2桁なら、最上位桁を繰り上げ
    if digits == 2:
        return (int(str_val[0])+1) * 10

    # 3桁以上なら、最上位桁の1つ低い桁を繰り上げ
    ceil_val =   int(str_val[0])    * 10**(digits-1)
    ceil_val += (int(str_val[1])+1) * 10**(digits-2)
    
    return ceil_val

# +
columns = [extract_pattern(category, column) for category in VMSTAT_COLUMNS.keys() for column in VMSTAT_COLUMNS[category].keys()]

# timestamp regex (YYYY-mm-dd HH:MM:SS)
timestamp_regex = r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}"

# 列分割用正規表現
EXTRACT_PATTERN = r"^\s*?" + r"\s+?".join(columns) + r"\s+" + f"(?P<timestamp>{timestamp_regex})" + r".*$"

# +
# log名
# Jupyter/IPython経由の場合は、カレントディレクトリから見つかった"pidstat.log"を使用
try:
    get_ipython()
except NameError:
    log_path = sys.argv[1]
else:
    import glob
    log_path = "vmstat.log"

# ファイルパス(拡張子なし), 拡張子
file_path, ext = os.path.splitext(log_path[0])

# 出力先、ファイル
path_name, file_name = os.path.split(file_path)

# +
# road file
vmstat_df = pd.read_csv(log_path, header=None)

# extract subjects
vmstat_df = vmstat_df[vmstat_df[0].str.match(r"^\s*\d")]

# split columns
vmstat_df = vmstat_df[0].str.extract(EXTRACT_PATTERN).reset_index(drop=True)

# convert value type
convert_type(vmstat_df)

# set datetime index
vmstat_df.set_index('timestamp', inplace=True, drop=True)

# convert multiindex
index_tuples = [(category, column) for category in VMSTAT_COLUMNS.keys() for column in VMSTAT_COLUMNS[category].keys()]
vmstat_df.columns = pd.MultiIndex.from_tuples(index_tuples, names=["category", "column"])

vmstat_df
# -

# ## Process Info

# +
# 画像ファイルパス
proc_file = os.path.join(path_name, "vmstat_proc.png")

# ymax
y_max = ceiling(vmstat_df['proc'].max())

# 画像出力
ax = vmstat_df['proc'].plot(alpha=0.8, figsize=(20, 15))
ax.set_ylim(0, y_max)
ax.set_yticks(np.linspace(0, y_max, 11))
ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
ax.set_title("Process Information")

ax.set_ylabel("Run Queue/Blocking processes")
ax.set_xlabel("Test elapsed time")
plt.savefig(proc_file, bbox_inches='tight')
# -

# ## MEM Usage

# +
# 画像ファイルパス
mem_usage_file = os.path.join(path_name, "vmstat_mem_usage.png")

# ymax
y_max = ceiling(vmstat_df['memory'].sum(axis=1))

# 画像出力
ax = vmstat_df['memory'].plot(kind="area", alpha=0.7, figsize=(20, 15))
ax.set_ylim(0, y_max)
ax.set_yticks(np.linspace(0, y_max, 11))
ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
ax.set_title("MEM Usage [KB]")
ax.set_ylabel("MEM Usage [KB]")
ax.set_xlabel("Test elapsed time")
plt.savefig(mem_usage_file, bbox_inches='tight')
# -

# ## Swapping

# +
# 画像ファイルパス
swapping_file = os.path.join(path_name, "vmstat_swapping.png")

# ymax
y_max = ceiling(vmstat_df['swap'].max())

# 画像出力
ax = vmstat_df['swap'].plot(alpha=0.8, figsize=(20, 15))
ax.set_ylim(0, y_max)
ax.set_yticks(np.linspace(0, y_max, 11))
ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
ax.set_title("Swapping")

ax.set_ylabel("Swap IN/OUT")
ax.set_xlabel("Test elapsed time")
plt.savefig(swapping_file, bbox_inches='tight')
# -

# ## Disk I/O

# +
# 画像ファイルパス
disk_io_file = os.path.join(path_name, "vmstat_disk_io.png")

# ymax
y_max = ceiling(vmstat_df['io'].max())

# 画像出力
ax = vmstat_df['io'].plot(alpha=0.8, figsize=(20, 15))
ax.set_ylim(0, y_max)
ax.set_yticks(np.linspace(0, y_max, 11))
ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
ax.set_title("Disk I/O (Block count)")
ax.set_ylabel("Block count")
ax.set_xlabel("Test elapsed time")
plt.savefig(disk_io_file, bbox_inches='tight')
# -

# ## System Info

# +
# 画像ファイルパス
sysinfo_file = os.path.join(path_name, "vmstat_system_info.png")

# ymax
y_max = ceiling(vmstat_df['system'].max())

# 画像出力
ax = vmstat_df['system'].plot(alpha=0.8, figsize=(20, 15))
ax.set_ylim(0, y_max)
ax.set_yticks(np.linspace(0, y_max, 11))
ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
ax.set_title("System Information (Context Switch/Interruption)")
ax.set_ylabel("Context Switch & Interruption")
ax.set_xlabel("Test elapsed time")
plt.savefig(sysinfo_file, bbox_inches='tight')
# -

# ## CPU Usage

# +
# 画像ファイルパス
cpu_usage_file = os.path.join(path_name, "vmstat_cpu_usage.png")

# ymax
y_max = 100

# 画像出力
ax = vmstat_df['cpu'].plot(kind="area", alpha=0.8, stacked=True, figsize=(20, 15))
ax.set_ylim(0, y_max)
ax.set_yticks(np.linspace(0, y_max, 11))
ax.yaxis.set_major_formatter(ticker.PercentFormatter())
ax.set_title("CPU Usage")
ax.set_ylabel("CPU Usage")
ax.set_xlabel("Test elapsed time")
plt.savefig(cpu_usage_file, bbox_inches='tight')

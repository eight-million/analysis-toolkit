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

PIDSTAT_COLUMNS = dict([
    ("timestamp",         INT_VALUE),
    ("uid",               INT_VALUE),
    ("pid",               INT_VALUE),
    ("user_usage",        FLOAT_VALUE),
    ("system_usage",      FLOAT_VALUE),
    ("guest_usage",       FLOAT_VALUE),
    ("total_cpu_usage",   FLOAT_VALUE),
    ("used_cpu_core",     INT_VALUE),
    ("minor_fault",       FLOAT_VALUE),
    ("major_fault",       FLOAT_VALUE),
    ("virtual_size",      INT_VALUE),
    ("resident_set_size", INT_VALUE),
    ("memory_usage",      FLOAT_VALUE),
    ("stack_size",        INT_VALUE),
    ("stack_refs",        INT_VALUE),
    ("kB_read",           FLOAT_VALUE),
    ("kB_write",          FLOAT_VALUE),
    ("kB_canceled_write", FLOAT_VALUE),
    ("context_switch",    FLOAT_VALUE),
    ("nv_context_switch", FLOAT_VALUE),
])

def extract_pattern(header):
    return f"(?P<{header}>{PIDSTAT_COLUMNS[header]['regex']})"

def convert_type(df):
    for header, value_type in PIDSTAT_COLUMNS.items():
        df[header] = df[header].astype(value_type['type'])

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

EXTRACT_PATTERN = r"^\s+?" + r"\s+?".join([extract_pattern(header) for header in PIDSTAT_COLUMNS.keys()]) + r".*"

# +
# log名
# Jupyter/IPython経由の場合は、カレントディレクトリから見つかった"pidstat.log"を使用
try:
    get_ipython()
except NameError:
    log_path = sys.argv[1]
else:
    import glob
    log_path = "pidstat.log"

# ファイルパス(拡張子なし), 拡張子
file_path, ext = os.path.splitext(log_path[0])

# 出力先、ファイル
path_name, file_name = os.path.split(file_path)

# +
# road file
pidstat_df = pd.read_csv(log_path, header=None)

# extract subjects
pidstat_df = pidstat_df[pidstat_df[0].str.match(r"^\s+\d")]

# split columns
pidstat_df = pidstat_df[0].str.extract(EXTRACT_PATTERN).reset_index(drop=True)

# convert value type
convert_type(pidstat_df)

# convert timestamp from UNIX epoch to JST
pidstat_df['timestamp'] = pd.to_datetime(pidstat_df['timestamp'], unit='s', utc=True).apply(lambda t: t.tz_convert('Asia/Tokyo'))

# set datetime index
pidstat_df.set_index('timestamp', inplace=True, drop=True)
pidstat_df
# -

# ##  CPU Usage

# +
# 画像ファイルパス
cpu_usage_file = os.path.join(path_name, "pidstat_cpu_usage.png")

# 画像出力
ax = pidstat_df[['user_usage', 'system_usage', 'guest_usage']].plot(kind="area", stacked=True, alpha=0.8, figsize=(20, 15))
ax.set_ylim(0, 100)
ax.set_yticks(np.linspace(0, 100, 11))
ax.yaxis.set_major_formatter(ticker.PercentFormatter())
ax.set_title("CPU Usage")

ax.set_ylabel("CPU Usage")
ax.set_xlabel("Test elapsed time")
plt.savefig(cpu_usage_file, bbox_inches='tight')
# -

# ## MEM Usage

# +
# 画像ファイルパス
mem_usage_file = os.path.join(path_name, "pidstat_mem_usage.png")

# ymax
vsz_ymax = ceiling(pidstat_df['virtual_size'])
rss_ymax = ceiling(pidstat_df['resident_set_size'])
y_max = max(vsz_ymax, rss_ymax)

# 画像出力
ax = pidstat_df[['virtual_size', 'resident_set_size']].plot(kind="area", stacked=False, alpha=0.7, figsize=(20, 15))
ax.set_ylim(0, y_max)
ax.set_yticks(np.linspace(0, y_max, 11))
ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
ax.set_title("MEM Usage [KB]")
ax.set_ylabel("MEM Usage [KB]")
ax.set_xlabel("Test elapsed time")
plt.savefig(mem_usage_file, bbox_inches='tight')
# -

# ## Page Fault

# +
# 画像ファイルパス
page_fault_file = os.path.join(path_name, "pidstat_page_fault_counts.png")

# ymax
minor_ymax = ceiling(pidstat_df['minor_fault'])
major_ymax = ceiling(pidstat_df['major_fault'])
y_max = max(minor_ymax, major_ymax)

# 画像出力
ax = pidstat_df[['minor_fault', 'major_fault']].plot(alpha=0.8, figsize=(20, 15))
ax.set_ylim(0, y_max)
ax.set_yticks(np.linspace(0, y_max, 11))
ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
ax.set_title("Minor/Major Fault per second")
ax.set_ylabel("Fault counts")
ax.set_xlabel("Test elapsed time")
plt.savefig(page_fault_file, bbox_inches='tight')
# -

# ## Context Switches

# +
# 画像ファイルパス
cswt_file = os.path.join(path_name, "pidstat_context_switch_counts.png")

# ymax
cswt_ymax = ceiling(pidstat_df['context_switch'])
nv_cswt_ymax = ceiling(pidstat_df['nv_context_switch'])
y_max = max(cswt_ymax, nv_cswt_ymax)

# 画像出力
ax = pidstat_df[['context_switch', 'nv_context_switch']].plot(alpha=0.8, figsize=(20, 15))
ax.set_ylim(0, y_max)
ax.set_yticks(np.linspace(0, y_max, 11))
ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
ax.set_title("Context switch counts per second")
ax.set_ylabel("Context switch")
ax.set_xlabel("Test elapsed time")
plt.savefig(cswt_file, bbox_inches='tight')
# -

# ## Stack Size

# +
# 画像ファイルパス
stack_file = os.path.join(path_name, "pidstat_stack_size.png")

# ymax
y_max = ceiling(pidstat_df[['stack_size', 'stack_refs']].max())

# 画像出力
ax = pidstat_df[['stack_size', 'stack_refs']].plot(alpha=0.8, figsize=(20, 15))
ax.set_ylim(0, y_max)
ax.set_yticks(np.linspace(0, y_max, 11))
ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
ax.set_title("Stack size and references")
ax.set_ylabel("Stack size/refs")
ax.set_xlabel("Test elapsed time")
plt.savefig(stack_file, bbox_inches='tight')
# -

# ## Disk I/O

# +
# 画像ファイルパス
disk_file = os.path.join(path_name, "pidstat_disk_io.png")

# ymax
y_max = ceiling(pidstat_df[['kB_read', 'kB_write', 'kB_canceled_write']].max())

# 画像出力
ax = pidstat_df[['kB_read', 'kB_write', 'kB_canceled_write']].plot(alpha=0.8, figsize=(20, 15))
ax.set_ylim(0, y_max)
ax.set_yticks(np.linspace(0, y_max, 11))
ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
ax.set_title("Disk I/O [KB]")
ax.set_ylabel("Disk I/O [KB]")
ax.set_xlabel("Test elapsed time")
plt.savefig(disk_file, bbox_inches='tight')

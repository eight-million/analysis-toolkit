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

import datetime
import os
import sys

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

plt.style.use("ggplot")

plt.rcParams["font.size"]= 20
plt.rcParams["xtick.labelsize"]=20
plt.rcParams["ytick.labelsize"]=20
plt.rcParams["figure.figsize"]=(20,15)

# +
# log名
# Jupyter/IPython経由の場合は、カレントディレクトリから見つかった"tps_datetimes.log"を使用
try:
    get_ipython()
except NameError:
    log_path = sys.argv[1]
else:
    log_path = "datetimes.log"

# ファイルパス(拡張子なし), 拡張子
file_path, ext = os.path.splitext(log_path[0])

# 出力先、ファイル
path_name, file_name = os.path.split(file_path)

df = pd.read_csv(log_path, parse_dates=["datetime"], names=["datetime"])
# -

# 0秒基準に
elapsed_index = pd.DatetimeIndex(df["datetime"]).to_perioddelta("T")
origin_s, origin_ms = elapsed_index[0].seconds, elapsed_index[0].microseconds
df["elapsed_time"] = elapsed_index - datetime.timedelta(seconds=origin_s, microseconds=origin_ms)

# 累積件数(cumsum)を追加
df["cumsum"] = df.index + 1

# +
# 秒(S)間隔でリサンプリング
df_per_sec = df.resample(rule="S", on="datetime").count()

# 移動平均(30個ずつ)も追加
df_per_sec["rolling_mean_30"] = df_per_sec["cumsum"].rolling(window=30, center=True).mean()
# -

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
fig, left = plt.subplots(figsize=(16, 9))

# 累積グラフ(赤線)
left_y_max = ceiling(df["cumsum"])
left.plot(pd.DatetimeIndex(df["datetime"]), df["cumsum"], "r-.x", label="cumulative sum")
left.set_xlabel("test time")
left.set_ylabel("cumsum")
left.set_ylim(0, left_y_max)
left.set_yticks(np.linspace(0, left_y_max, 11))
left.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))

# 単位時間(秒間)あたりのサンプル数(青線)
right_y_max = ceiling(df_per_sec["cumsum"])
right = left.twinx()
right.plot(df_per_sec["cumsum"], "b-.o", label="write per second")
right.set_ylabel("records per second")
right.set_ylim(0, right_y_max)
right.set_yticks(np.linspace(0, right_y_max, 11))
right.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))

# 移動平均(緑線)
right.plot(df_per_sec["rolling_mean_30"], "g-.+", label="rolling mean(window=30)")

# 凡例追加
fig.legend()
plt.savefig("./tps_datetimes.png")

# baccarat
# 🎴 百家樂策略模擬器 (Baccarat Strategy Simulator)

用蒙地卡羅方式模擬百家樂,比較不同下注策略的長期表現,並以 `matplotlib` 畫出結果。

> 想知道「馬丁格爾」真的能穩贏嗎?跑幾千局就知道了。

## ✨ 特色

- 完整實作百家樂**抽牌與補牌規則**(閒家、莊家第三張牌)
- 多副牌牌靴(預設 8 副),並有「切牌卡」位置自動洗牌
- 內建 6 種策略,也可傳入**自訂策略函式**
- 可調整賠率、莊家抽水、桌限、目標獲利等參數
- 兩種分析模式:
  - `do1time()`:同一牌局下所有策略同場比較
  - `focus_on()`:針對單一策略重複模擬多次,看最終資金分佈或走勢

## 📦 安裝

需要 **Python 3.10+**(程式使用了 `str | FunctionType` 型別語法)。

```bash
pip install matplotlib
```

## ▶️ 執行

```bash
python baccarat.py
```

> ⚠️ 檔案底部有示範程式,**直接執行或 import 時都會跑**。若要當模組使用,請把示範區包進 `if __name__ == "__main__":`。

## 🎯 內建策略

| 名稱 | 說明 |
|------|------|
| `always banker` | 永遠押莊 |
| `always player` | 永遠押閒 |
| `always tie` | 永遠押和 |
| `random choose` | 隨機押(20% 和、40% 莊、40% 閒) |
| `gambler think` | 賭徒謬誤:上一把是閒就押莊,否則押閒 |
| `martingale` | 馬丁格爾:首次隨機選邊並持續押同一邊,輸了加倍、贏了回到基礎注 |

## ⚙️ 設定

設定區位於檔案開頭:

```python
DEFAULT_MONEY = 10000         # 起始籌碼
END_MONEY = 20000             # 任一方資金達標即結束(None = 不限)
DEFAULT_BET = 100             # 一般策略的基礎押注
MARTINGALE_DEFAULT_BET = 100  # 馬丁格爾的基礎押注
TABLE_LIMIT = 5000            # 牌桌下注上限(None = 不限)
RESHUFFLE_AT = 70             # 牌靴剩幾張時重新洗牌
HOW_MANY_DECKS = 8            # 幾副牌
THE_TIE_WIN_TIMES = 8         # 押和賠率(8 賠 1)
CASINO_BANKER_TAX = 0.05      # 押莊贏時的抽水(5%)
TIMES = 160                   # 一個大局最多玩幾手
```

## 📖 使用方式

### 1. 所有策略同場比較

```python
do1time()                          # 畫出所有策略的資金曲線
history = do1time(print_it=False, return_it=True)  # 只回傳資料
```

### 2. 針對單一策略重複模擬

```python
# 馬丁格爾跑 100 次,取平均最終資金
result = focus_on("martingale", 100)
print(result["average_money"])

# 畫出 100 次的最終資金分佈直方圖
focus_on("gambler think", 100, show_it=True, return_it=False)

# 畫出 1000 次的資金走勢線
focus_on("always tie", 1000, return_each_history=True, show_it=True, return_it=False)
```

`focus_on(strategy, times, return_each_history=False, show_it=False, return_it=True)`

| 參數 | 說明 |
|------|------|
| `strategy` | 內建策略名稱字串,或自訂函式 |
| `times` | 要模擬幾個大局 |
| `return_each_history` | `True` 回傳每局走勢,`False` 回傳統計摘要 |
| `show_it` | 是否畫圖 |
| `return_it` | 是否回傳結果 |

統計摘要格式:

```python
{
    "get_top": 12,            # 達到 END_MONEY 的次數
    "money_empty": 5,         # 破產次數
    "money_list": [...],      # 每局最終資金
    "average_money": 9876.5   # 平均最終資金
}
```

### 3. 自訂策略

寫一個回傳 `("選擇", 押注金額)` 的函式即可,選擇為 `"banker"`、`"player"` 或 `"tie"`:

```python
def my_strategy():
    # 例:莊閒交替押,每次 200
    return ("banker" if last_win == "player" else "player", 200)

focus_on(my_strategy, 500, show_it=True, return_it=False)
```

> 自訂策略可讀取全域變數 `last_win`(上一把的結果)。

## 🎲 規則摘要

- 牌值:A~9 為面值,10、J、Q、K 為 0,總和取個位數
- 任一方前兩張牌為 8 或 9(天牌)時雙方不補牌
- 閒家 0~5 點補牌、6~7 點停牌;莊家依閒家第三張牌決定是否補牌
- **賠率**:押閒 1:1;押莊 1:0.95(抽 5% 水);押和 8:1;開和時押莊閒退回本金

## 📊 觀察重點

- 長期來看,莊、閒、和各自都有賭場優勢,**沒有任何下注法能改變期望值**
- 馬丁格爾在短期看似常贏,但遇到連敗會碰到**桌限**與**資金上限**而爆倉
- 押和賠率高、變異大,平均結果最差

## ⚠️ 免責聲明

本專案僅供**程式與機率學習**,模擬結果不代表真實賭場表現,也不構成任何賭博建議。請理性看待賭博風險。

## 📄 授權

請依需求自行加入 LICENSE(例如 MIT)。

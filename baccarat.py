from random import shuffle,random
import matplotlib.pyplot as plt
from types import FunctionType

####################################################
#            設定區(此為建議設定值)

# 預設籌碼
DEFAULT_MONEY = 10000
# 在任意一方 有多少錢 時 立刻結束 (輸入None代表沒有)
END_MONEY = 20000

# 大家的 基礎押注
DEFAULT_BET   = 100
# 馬丁格爾 基礎押注
MARTINGALE_DEFAULT_BET = 100
# 牌桌下注上限 (輸入None代表沒有)
TABLE_LIMIT = 5000

# 重新洗牌卡 放第幾張
RESHUFFLE_AT = 70
# 要放幾副牌
HOW_MANY_DECKS = 8

# 押和 的賠率
THE_TIE_WIN_TIMES = 8
# 押莊的抽水
CASINO_BANKER_TAX = 0.05

#次數(一個大局玩到幾局時強制結束)
TIMES = 160

####################################################


last_win=""

deck=[]
def resetdeck()->None:
    '''重設牌堆'''
    global deck
    deck=[1,2,3,4,5,6,7,8,9,0,0,0,0]*4*HOW_MANY_DECKS
    shuffle(deck)
def getcard()->int:
    '''從排堆抽第一張牌，回傳'''
    return deck.pop(0)

class strategy:
    '''策略們'''
    def __init__(self):
        self.inside_strategys=[
            self.always_banker,
            self.always_player,
            self.always_tie,
            self.random_choose,
            self.gambler_think,
            self.martingale]
        self.inside_strategys_str=[
            "always banker",
            "always player",
            "always tie",
            "random choose",
            "gambler think",
            "martingale"]
        self.money=[DEFAULT_MONEY]*len(self.inside_strategys)
        self.martingale_bet=MARTINGALE_DEFAULT_BET
        self.martingale_tobet="player" if random()>=0.5 else "banker"

    def always_banker(self):
        """永遠選擇押莊"""
        return ("banker",DEFAULT_BET)
    def always_player(self):
        """永遠選擇押閒"""
        return ("player",DEFAULT_BET)
    def always_tie(self):
        """永遠選擇押和"""
        return ("tie",DEFAULT_BET)
    def random_choose(self):
        """隨機押(20%和, 40%莊, 40%閒)"""
        todo="tie" if random()>=0.8 else "banker" if random()>=0.5 else "player"
        return(todo,DEFAULT_BET)
    def gambler_think(self):
        """如果上一個是莊則押閒，否則押莊"""
        return (("banker" if last_win=="player" else "player"),DEFAULT_BET)
    def martingale(self):
        """第一次隨機，持續押，但是押注大小會越輸越大"""
        return (self.martingale_tobet,self.martingale_bet)
strategys = strategy()

resetdeck()

def know_who_win()->str:
    '''回傳勝利者'''
    #抽牌
    banker = (getcard()+getcard())%10
    player = (getcard()+getcard())%10
    #補牌
    if not (banker>=8 or player>=8):
        player_get = False
        if player<=5:
            player_get=getcard()
            player = (player+player_get)%10
        if player_get:
            if (
                (banker<=2) or
                (banker==3 and player_get!=8) or
                (banker==4 and 1<player_get<8)or
                (banker==5 and 3<player_get<8)or
                (banker==6 and 5<player_get<8)
            ): banker = (banker+getcard())%10
        else:
            if banker<=5:
                banker = (banker+getcard())%10
    #比對勝負
    return "tie" if banker==player else "banker" if banker>player else "player"

def reset_everything():
    """重置所有全域狀態"""
    global deck, last_win, strategys, money

    resetdeck()

    last_win = ""

    strategys.money = [DEFAULT_MONEY] * len(strategys.inside_strategys)
    strategys.martingale_bet = MARTINGALE_DEFAULT_BET
    strategys.martingale_tobet = "player" if random() >= 0.5 else "banker"

    money=DEFAULT_MONEY

def do1time_main():
    '''do1time 的 主程式'''
    #是否洗牌
    if len(deck)<=RESHUFFLE_AT:
        resetdeck()
    which_win = know_who_win()
    #給錢
    if which_win=="tie":
        for i in range(len(strategys.inside_strategys)):
            if strategys.money[i]<=0: strategys.money[i]=0;continue
            this_time_todo = strategys.inside_strategys[i]()
            bet=min(this_time_todo[1],strategys.money[i])
            if TABLE_LIMIT: bet=min(bet,TABLE_LIMIT)
            if this_time_todo[0]=="tie":
                strategys.money[i] += bet*THE_TIE_WIN_TIMES
            # 否則退錢
    else:
        for i in range(len(strategys.inside_strategys)):
            if strategys.money[i]<=0: strategys.money[i]=0;continue
            this_time_todo = strategys.inside_strategys[i]()
            bet=min(this_time_todo[1],strategys.money[i])
            if TABLE_LIMIT: bet=min(bet,TABLE_LIMIT)
            if this_time_todo[0]==which_win:
                strategys.money[i] += bet*((1-CASINO_BANKER_TAX) if which_win=="banker" else 1) # type: ignore
                if strategys.inside_strategys[i]==strategys.martingale:
                    strategys.martingale_bet = MARTINGALE_DEFAULT_BET
            else:
                strategys.money[i] -= bet
                if strategys.inside_strategys[i]==strategys.martingale:
                    strategys.martingale_bet*=2
        global last_win ; last_win = which_win

# 執行 1 次
def do1time(print_it:bool=True,return_it:bool=False):
    '''讓所有策略跑一次，如果print_it會印出圖表
    如果return_it會回傳整個list'''
    reset_everything()
    money_history=[[] for _ in range(len(strategys.inside_strategys))]
    for _ in range(TIMES):
        do1time_main()
        for i in range(len(strategys.inside_strategys)):
            strategys.money[i] = 0 if strategys.money[i]<0 else strategys.money[i]
            money_history[i].append(strategys.money[i])
        stop=False
        if len(strategys.inside_strategys)-strategys.money.count(0)<=1:
            stop=True
        for i in strategys.money:
            if not END_MONEY:break
            if i>=END_MONEY:stop=True
        if stop:break
    for i in range(len(money_history)):
        plt.plot(money_history[i], label=strategys.inside_strategys_str[i])
    if print_it:
        plt.axhline(DEFAULT_MONEY, linestyle="--")
        plt.legend()
        plt.grid(True)
        plt.xlabel("Round")
        plt.ylabel("Money")
        plt.show()
        print()
    if return_it:
        return money_history

# 瞄準 1 個策略測試幾次
def focus_on(
        strategy_to_focus:str|FunctionType,
        times:int,
        return_each_history: bool = False,
        show_it: bool = False,
        return_it:bool=True)->dict|list|None:
    '''strategy_to_focus請輸入[
    "always banker",
    "always player",
    "always tie",
    "random choose",
    "gambler think",
    "martingale"
    ]中的一個 or 回傳格式為("選擇",押注)的任意函式

    times是觀察幾局(大局)

    return_each_history是回傳值&印出值是否為每一次的money_history

    show_it是要不要畫圖

    return_it是要不要回傳'''
    end_history={
        "get_top":0,
        "money_empty":0,
        "money_list":[]
    }


    if callable(strategy_to_focus):
        strategy_func = strategy_to_focus
        strategy_name = strategy_func.__name__
    elif strategy_to_focus in strategys.inside_strategys_str:
        idx = strategys.inside_strategys_str.index(strategy_to_focus)
        strategy_func = strategys.inside_strategys[idx]
        strategy_name = strategy_to_focus
    else:
        raise ValueError("不存在本策略")


    history_to_plot = []

    for _ in range(times):
        reset_everything()

        money = DEFAULT_MONEY

        current_trial_history = []

        for _ in range(TIMES):
            if money<=0:
                money=0
                end_history["money_empty"]+=1
                if return_each_history: current_trial_history.append(money)
                break
            if END_MONEY:
                if money>=END_MONEY:
                    end_history["get_top"]+=1
                    if return_each_history: current_trial_history.append(money)
                    break

            #是否洗牌
            if len(deck)<=RESHUFFLE_AT:
                resetdeck()
            which_win = know_who_win()

            #給錢
            todo=strategy_func()
            bet=todo[1]
            bet = min(bet,money)
            if TABLE_LIMIT:
                bet=min(bet,TABLE_LIMIT)

            if which_win=="tie":
                if which_win == todo[0]:
                    money += bet * THE_TIE_WIN_TIMES
                # 否則退錢
            else:
                if which_win == todo[0]:
                    money += bet*(1-CASINO_BANKER_TAX*(which_win=="banker"))
                else:
                    money -= bet
            last_win=which_win

            if return_each_history:
                current_trial_history.append(money)

        end_history["money_list"].append(money)

        if return_each_history:
            history_to_plot.append(current_trial_history)

    end_history["average_money"] = sum(end_history["money_list"])/len(end_history["money_list"])

    # 繪圖邏輯
    if show_it:
        plt.figure(figsize=(10, 6))

        if not return_each_history:
            # 畫出直方圖 (分佈)
            plt.hist(end_history["money_list"], bins=20, color='skyblue', edgecolor='black', alpha=0.7)
            plt.axvline(DEFAULT_MONEY, color='red', linestyle='--', linewidth=2, label=f'Default: {DEFAULT_MONEY}')
            avg_m = end_history["average_money"]
            plt.axvline(avg_m, color='green', linestyle='-', linewidth=2, label=f'Average: {avg_m:.0f}')
            plt.title(f"Final Money Distribution ({times} trials)\nStrategy: {strategy_name}", fontsize=14)
            plt.xlabel("Remaining Money", fontsize=12)
            plt.ylabel("Number of Trials (Frequency)", fontsize=12)
            plt.legend()
            plt.grid(axis='y', alpha=0.3)

        else:
            # 畫出折線圖 (過程)
            # --- 修正點 4: 使用正確的歷史紀錄變數繪圖 ---
            for history in history_to_plot:
                # 為了避免線條太亂，使用透明度 alpha
                plt.plot(history, alpha=0.2, linewidth=0.5)

            plt.axhline(DEFAULT_MONEY, color='black', linestyle='--', label='Initial Capital')
            plt.title(f"Detailed Trends ({times} trials)\nStrategy: {strategy_name}")
            plt.xlabel("Round (In-game)")
            plt.ylabel("Money")
            plt.grid(True, alpha=0.3)
            plt.legend()

        plt.show()
        print()

    # 回傳邏輯
    if return_it:
        if return_each_history:
            return history_to_plot
        else:
            return end_history

#    示範程式
do1time()
print("\n馬丁格爾的賭徒平均結果：",focus_on("martingale",100)["average_money"],"\n") # type: ignore
focus_on("gambler think",100,show_it=True,return_it=False)
focus_on("always tie",1000,return_each_history=True,show_it=True,return_it=False)
focus_on("always player",1000,return_each_history=True,show_it=True,return_it=False)

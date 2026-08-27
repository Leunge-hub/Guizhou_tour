import tkinter
import random
import os
import sys
from PIL import Image, ImageTk

# 定義取得圖片路徑的函式
def get_image_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(r"C:\Users\user\Downloads\朱老師貴州旅行", filename)


img = [None] * 14
card = [0] * 26
face = [0] * 26
memo = [0] * 26
img_back_l2 = None # 儲存第二關專屬卡牌背面 (0_level2.png)
bg_img1 = None     # 第一關背景大合照 (bg.png)
bg_img2 = None     # 第二關背景大合照 (bg2.png)
stage = 1  # 🌟 關卡標籤：1 代表 Level 1，2 代表 Level 2
use_photo_bg = False  # True 表示當前是大合照背景，False 表示純色

# 🌟【新增這行】控制是否已點擊背景按鈕
bg_button_clicked = False

# 結算醒目大字字體 (微軟正黑體，32號加粗)
WIN_FNT = ("Microsoft JhengHei", 32, "bold")

proc = 0
tmr = 0
sel1 = 0
sel2 = 0
player = 0
computer = 0

# 1. 卡牌尺寸 (130x195 符合 2:3 比例)
CARD_W = 130
CARD_H = 195

# 2. 網格單元格尺寸
CELL_W = 138
CELL_H = 195

# 3. 字體大小
FNT = ("Times New Roman", 46)

def draw_card():
    csv.delete("all")
    
    # 1. 根據設定繪製背景
    if use_photo_bg:
        current_bg = bg_img1 if stage == 1 else bg_img2
        if current_bg:
            csv.create_image(0, 0, image=current_bg, anchor="nw")

    # 2. 繪製卡牌
    if proc != 0:
        for i in range(26):
            # 若 face[i] == 2 (配對成功消除)，直接跳過不畫
            if face[i] == 2:
                continue

            x = (i % 7) * CELL_W + CELL_W // 2
            y = int(i / 7) * CELL_H + CELL_H // 2

            # 蓋牌狀態：根據關卡顯示卡牌背面
            if face[i] == 0:
                if stage == 2 and img_back_l2:
                    csv.create_image(x, y, image=img_back_l2) # 第二關特製背面
                else:
                    csv.create_image(x, y, image=img[0])       # 第一關卡牌背面
            
            # 翻開狀態：直接顯示圖片
            elif face[i] == 1:
                csv.create_image(x, y, image=img[card[i]])


def shuffle_card():
    for i in range(26):
        card[i] = 1 + i % 13
        face[i] = 0
        memo[i] = 0
    
    # 洗牌：只打亂卡牌 ID，不再區分卡牌類型
    for i in range(100):
        r1 = random.randint(0, 12)
        r2 = random.randint(13, 25)
        card[r1], card[r2] = card[r2], card[r1]

# 🌟 翻第一張牌：優先開 memo 中已知成對的，沒有就隨機選
def com_select1():
    for i in range(25):
        for j in range(i + 1, 26):
            if memo[i] > 0 and memo[i] == memo[j] and face[i] == 0 and face[j] == 0:
                return i

    unopened = [i for i in range(26) if face[i] == 0]
    return random.choice(unopened) if unopened else 0

# 🌟 翻第二張牌：拿第一張牌的數字去 memo 找匹配卡，沒有就隨機選
def com_select2(first_card_idx):
    target_num = card[first_card_idx]
    
    # 在 memo 搜尋是否有與第一張配對的牌
    for i in range(26):
        if i != first_card_idx and memo[i] == target_num and face[i] == 0:
            return i

    unopened = [i for i in range(26) if face[i] == 0 and i != first_card_idx]
    return random.choice(unopened) if unopened else first_card_idx
        

def click(e):
    global proc, tmr, sel1, sel2, player, computer, stage,use_photo_bg, bg_button_clicked
    
    # # 🧪 【測試 1：點右上角】觸發「玩家勝利」
    # if 1 <= proc <= 6 and e.x > 1000 and e.y < 200:
    #     player = 26
    #     computer = 0
    #     proc = 7
    #     tmr = 0
    #     return

    # # 🧪 【測試 2：點右側 COM 區】觸發「玩家失敗」
    # if 1 <= proc <= 6 and e.x > 1000 and 400 <= e.y <= 600:
    #     player = 0
    #     computer = 26
    #     proc = 7
    #     tmr = 0
    #     return

    # 開局點擊
    if proc == 0:
        # 1. 點擊正中央的切換背景按鈕 (X: 300~900, Y: 270~370)
        if 300 <= e.x <= 900 and 270 <= e.y <= 370:
            use_photo_bg = not use_photo_bg  # 切換背景狀態
            bg_button_clicked = True         # 標記已按過背景按鈕
            return

        # 2. 當背景按鈕點擊後，才會觸發 Level 1 / Level 2 選擇
        if bg_button_clicked:
            # 點擊 Level 1 按鈕 (X: 250~550, Y: 420~520)
            if 250 <= e.x <= 550 and 420 <= e.y <= 520:
                stage = 1
                shuffle_card()
                player = 0
                computer = 0
                proc = 1
                tmr = 0
                return

            # 點擊 Level 2 按鈕 (X: 650~950, Y: 420~520)
            if 650 <= e.x <= 950 and 420 <= e.y <= 520:
                stage = 2
                shuffle_card()
                player = 0
                computer = 0
                proc = 1
                tmr = 0
                return

    # 🌟 🌟 🌟 【核心修復】玩家翻牌邏輯 🌟 🌟 🌟
    if proc in [1, 2]:
        x = int(e.x / CELL_W)
        y = int(e.y / CELL_H)
        if 0 <= x <= 6 and 0 <= y <= 3:
            n = x + y * 7
            if n < 26 and face[n] == 0:
                if proc == 1:
                    face[n] = 1
                    sel1 = n
                    proc = 2
                elif proc == 2:
                    face[n] = 1
                    sel2 = n
                    proc = 3
                    tmr = 0
                return
        
    # 🌟 結算畫面點擊處理 (proc == 7)
    if proc == 7:
        if player > computer:
            msg = "✨ 太棒了！先下一城！😎\n不過第一關只是熱身，電腦在第二關會火力全開的！🔥\n敢不敢繼續挑戰 Level 2，證明你們的友誼很牢固？😈" if stage == 1 else "🎉恭喜你，打敗了電腦！🤩\n證明你們的友誼穩如泰山！😎\n看來貴州交流的回憶還深刻😘"
        else:
            msg = "😒慘慘！在貴州的回憶也太薄弱了吧？\n你們的友誼陷入危機😱，請重新回憶🙂，\n然後再次挑戰，證明你們的友誼非常牢固！加油😊" if stage == 1 else "🥺 差一點點就通關了！Level 2 的電腦確實有點厲害！\n別灰心，能來到 Level 2 已經很棒了！👍\n再挑戰一次，這次一定能戰勝電腦！加油！🔥"
        
        finish_typing_tmr = 5 + len(list(msg)) * 2
        show_button_tmr = finish_typing_tmr + 40

        if tmr < show_button_tmr:
            return

        if stage == 1 and player > computer:
            stage = 2
        elif stage == 1 and player <= computer:
            stage = 1
        elif stage == 2 and player > computer:
            stage = 1
        elif stage == 2 and player <= computer:
            stage = 2

        shuffle_card()
        player = 0
        computer = 0
        proc = 1
        tmr = 0
        return


def main():
    global proc, tmr, sel1, sel2, player, computer, stage
    
    tmr += 1 

    draw_card()
    
    stay_time = 40 if stage == 1 else 20

    # 開局提示與按鈕繪制 (proc == 0)
    if proc == 0:
        # 1. 正中央顯示切換背景按鈕
        csv.create_rectangle(300, 270, 900, 370, fill="ivory", outline="gold", width=5)
        csv.create_text(600, 320, text="Click to change background", fill="black", font=("Microsoft JhengHei", 26, "bold"), anchor="center")

        # 2. 點擊背景按鈕後，在其正下方彈出 Level 1 / Level 2 兩個按鈕
        if bg_button_clicked:
            # Level 1 按鈕
            csv.create_rectangle(250, 420, 550, 520, fill="ivory", outline="gold", width=5)
            csv.create_text(400, 470, text="Level 1", fill="deepskyblue", font=("Times New Roman", 40, "bold"), anchor="center")

            # 🌟【新增】中間閃爍的 "or" 文字
            if tmr % 20 < 10:
                csv.create_rectangle(550, 420, 660, 520, fill="ivory", outline="gold", width=5)
                csv.create_text(600, 470, text="or", fill="crimson", font=("Microsoft JhengHei", 36, "bold"), anchor="center")

            # Level 2 按鈕
            csv.create_rectangle(650, 420, 950, 520, fill="ivory", outline="gold", width=5)
            csv.create_text(800, 470, text="Level 2", fill="crimson", font=("Times New Roman", 40, "bold"), anchor="center")

   # 🌟 右側 Player 得分資訊欄 (玩家回合 proc: 1~3 時顯示天空藍背景與金框)
    if 1 <= proc <= 3:
        csv.create_rectangle(1030, 30, 1170, 190, fill="skyblue", outline="gold", width=5)
    else:                  # 非玩家回合：象牙白背景與銀框
        csv.create_rectangle(1030, 30, 1170, 190, fill="ivory", outline="silver", width=3)

    csv.create_text(1100, 75, text="player", fill="black", font=FNT)    
    csv.create_text(1100, 145, text=player, fill="black", font=FNT)

    # 🌟 右側 COM 得分資訊欄 (電腦回合 proc: 4~6 時顯示粉紅色背景與金框)
    if 4 <= proc <= 6:
        csv.create_rectangle(1030, 420, 1170, 580, fill="pink", outline="gold", width=5)
    else:                  # 非電腦回合：象牙白背景與銀框
        csv.create_rectangle(1030, 420, 1170, 580, fill="ivory", outline="silver", width=3)

    csv.create_text(1100, 465, text="COM", fill="black", font=FNT)    
    csv.create_text(1100, 535, text=computer, fill="black", font=FNT)
    
    # 玩家翻開兩張牌後的結算比對 (proc == 3)
    if proc == 3 and tmr == stay_time:
        if card[sel1] == card[sel2]:
            face[sel1] = 2
            face[sel2] = 2
            player += 2
            memo[sel1] = -1
            memo[sel2] = -1
            if player + computer == 26:
                proc = 7
                tmr = 0
            else:
                proc = 1
                tmr = 0
        else:
            face[sel1] = 0
            face[sel2] = 0
            
            # 🌟 玩家回合記憶區：
            if stage == 1:
                memo[sel1] = card[sel1]  # 第一關：只記玩家翻的第一張牌
            else:
                memo[sel1] = card[sel1]  # 第二關：玩家翻的兩張牌都記
                memo[sel2] = card[sel2]
                
            proc = 4
            tmr = 0

    # 🌟 修改點：電腦思考與翻第一張牌 (proc == 4)
    if proc == 4 and tmr == 5:
        sel1 = com_select1()
        face[sel1] = 1
        proc = 5
        tmr = 0

    # 🌟 修改點：電腦根據第一張牌去思考與翻第二張牌 (proc == 5)
    if proc == 5 and tmr == 5:
        sel2 = com_select2(sel1)
        face[sel2] = 1
        proc = 6
        tmr = 0

    # 電腦翻開兩張牌後的結算比對 (proc == 6)
    if proc == 6 and tmr == stay_time:
        if card[sel1] == card[sel2]:
            face[sel1] = 2
            face[sel2] = 2
            computer += 2
            memo[sel1] = -1
            memo[sel2] = -1
            if player + computer == 26:
                proc = 7
                tmr = 0
            else:
                proc = 4
                tmr = 0
        else:
            face[sel1] = 0
            face[sel2] = 0
            
            # 🌟 電腦回合記憶區：
            if stage == 1:
                memo[sel2] = card[sel2]  # 第一關：只記電腦自己翻的第二張牌
            else:
                memo[sel1] = card[sel1]  # 第二關：電腦自己翻的兩張牌都記
                memo[sel2] = card[sel2]
                
            proc = 1
            tmr = 0

    # ------------------ 結算語錄與過場提示詞 ------------------
    if proc == 7:
        target_x = 600
        start_x = 1300
        slide_progress = min(1.0, tmr / 10.0)
        current_x = start_x - (start_x - target_x) * slide_progress

        if player > computer:
            if stage == 1:
                full_msg = "✨ 太棒了！先下一城！😎\n不過第一關只是熱身，電腦在第二關會火力全開的！🔥\n敢不敢繼續挑戰 Level 2，證明貴州旅行的回憶很牢固？😈"
            else:
                full_msg = "🎉恭喜你，打敗了電腦！\n看來貴州旅行的回憶還很牢固！🤩是不是經常偷偷看照片回味呢？😎\n最後感謝你的游玩😘"
            box_fill, text_color = "navy", "Cyan"
        else:
            if stage == 1:
                full_msg = "😒慘敗！在貴州的回憶也太薄弱了吧？\n貴州旅行的回憶陷入了危機😱，請重新回憶🙂，\n然後再次挑戰，證明貴州旅行的回憶非常牢固！加油😊"
            else:
                full_msg = "🥺 差一點點就通關了！Level 2 的電腦確實很強！\n別灰心，能來到 Level 2 已經很棒了！👍\n再挑戰一次，這次一定能戰勝電腦！加油！🔥"
            box_fill, text_color = "maroon", "gold"

        msg_list = list(full_msg)
        total_chars = len(msg_list)
        char_count = max(1, (tmr - 5) // 2)
        current_msg = "".join(msg_list[:char_count])
        
        finish_typing_tmr = 5 + total_chars * 2
        show_button_tmr = finish_typing_tmr + 40

        if tmr <= show_button_tmr:
            csv.create_rectangle(
                current_x - 550, 270, current_x + 550, 510, 
                fill=box_fill, outline="gold" if box_fill == "navy" else "red", width=4
            )
            csv.create_text(
                current_x, 390, 
                text=current_msg, fill=text_color, font=WIN_FNT, justify="center", anchor="center"
            )

        if tmr >= show_button_tmr and (tmr % 20 < 12):
            csv.create_rectangle(820, 630, 1180, 710, fill="ivory", outline="gold", width=5)
            
            if stage == 1:
                next_text = "Click to Level 2" if player > computer else "Click to Restart"
            else:
                next_text = "Click to Restart" if player > computer else "Retry Level 2"
                
            csv.create_text(1000, 670, text=next_text, fill="black", font=("Times New Roman", 30, "bold"), anchor="center")

    root.after(50, main)

root = tkinter.Tk()
root.title("貴州交流回憶")
root.resizable(False, False)
root.bind("<Button>", click)

csv = tkinter.Canvas(width=1200, height=780, bg="ivory")
csv.pack()

# 載入背景大合照 (自動判斷 .jpg 或 .png)
bg_jpg1 = get_image_path("bg.jpg")
bg_png1 = get_image_path("bg.png")
bg_path1 = bg_jpg1 if os.path.exists(bg_jpg1) else (bg_png1 if os.path.exists(bg_png1) else None)

bg_jpg2 = get_image_path("bg2.jpg")
bg_png2 = get_image_path("bg2.png")
bg_path2 = bg_jpg2 if os.path.exists(bg_jpg2) else (bg_png2 if os.path.exists(bg_png2) else None)

if bg_path1:
    pil_bg1 = Image.open(bg_path1)
    bg_img1 = ImageTk.PhotoImage(pil_bg1.resize((1200, 780), Image.Resampling.LANCZOS))

if bg_path2:
    pil_bg2 = Image.open(bg_path2)
    bg_img2 = ImageTk.PhotoImage(pil_bg2.resize((1200, 780), Image.Resampling.LANCZOS))

# 載入卡牌圖片 (0.jpg/png ~ 13.jpg/png)
for i in range(14):
    jpg_path = get_image_path(f"{i}.jpg")
    png_path = get_image_path(f"{i}.png")
    file_path = jpg_path if os.path.exists(jpg_path) else (png_path if os.path.exists(png_path) else None)

    if file_path:
        pil_img = Image.open(file_path)
        img[i] = ImageTk.PhotoImage(pil_img.resize((CARD_W, CARD_H), Image.Resampling.LANCZOS))

# 載入第二關卡牌背面 (0_level2.png / 0_level2.jpg)
jpg_l2 = get_image_path("0_level2.jpg")
png_l2 = get_image_path("0_level2.png")
file_l2 = jpg_l2 if os.path.exists(jpg_l2) else (png_l2 if os.path.exists(png_l2) else None)

if file_l2:
    pil_l2 = Image.open(file_l2)
    img_back_l2 = ImageTk.PhotoImage(pil_l2.resize((CARD_W, CARD_H), Image.Resampling.LANCZOS))

main()
root.mainloop()
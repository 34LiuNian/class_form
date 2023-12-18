import json
from datetime import datetime, date
from tkinter import *
from tkinter import messagebox
from time import sleep


class Calendar:
    def __init__(self):
        """
        初始化参数
        """
        self.root_x = 0  # 窗口 x
        self.root_y = 10  # 窗口 y
        self.x = 10  # 课表左右留空
        self.y = 10  # 课表上下留空
        self.width = 0  # 窗口宽度
        self.height = 0  # 窗口高度
        self.classes = []  # 课程
        self.labels = []  # 课程 label
        self.left = []  # 分隔符
        self.left_labs = []  # 分隔符 label
        self.selects = []  # 换课选项
        self.select_labs = None  # 换课 label
        self.times = []  # 课程时间
        self.selected = False  # 选中状态，False 表示未选中，数字表示选中的位置
        self.window = None  # 窗口主体
        self.now_class = 0  # 当前课程
        self.onw = ""  # 上课提示
        self.off_w = ""  # 下课提示
        self.status = False  # 上/下课
        self.off_tk = []  # 下课窗口
        self.font = ('仿宋', 40)  # 课表字体
        self.speed = 1  # 课表动画速度
        self.stop_update = False  # 考试判断
        self.transparency = 0.9  # 透明度
        self.x_list = None

    def move(self, wins, hope_l, hope_w, hope_x, hope_y, times=1.2):
        """
        平滑动画
        :param wins:
        :param hope_l: 期望窗口高度
        :param hope_w: 期望窗口宽度
        :param hope_x: 期望窗口x坐标
        :param hope_y: 期望窗口y坐标
        :param times: 动画倍速
        :return:
        """
        times *= 1 / self.speed
        length = []
        width = []
        x = []
        y = []
        win = []
        for b in range(len(wins)):
            length.append(wins[b].winfo_width())
            width.append(wins[b].winfo_height())
            x.append(wins[b].winfo_x())
            y.append(wins[b].winfo_y())
            a = -5
            while a < 5:
                length_now = -(length[b] - hope_l[b]) / (1 + 3 ** (-a)) + length[b]
                width_now = -(width[b] - hope_w[b]) / (1 + 3 ** (-a)) + width[b]

                x_now = -(x[b] - hope_x[b]) / (1 + 3 ** (-a)) + x[b]
                y_now = -(y[b] - hope_y[b]) / (1 + 3 ** (-a)) + y[b]

                win.append(str(int(length_now)) + "x" + str(int(width_now)) + "+" + str(int(x_now)) + "+" + str(
                    int(y_now)))
                a += 10 / int(times / 0.005)

        b = 1
        while b < int(times / 0.005):
            for a in range(len(wins)):
                wins[a].geometry(win[b + int(times / 0.005) * a])
                wins[a].update()
            sleep(0.005)
            b += 1

    def load_config(self, day=None):
        """
        读取配置文件
        :param day:指定读取的星期课表，若为None则自动读取当天的课表
        :return: pass
        """
        today = datetime.now()
        to_week = date(today.year, today.month, today.day).weekday()
        week = ["一", "二", "三", "四", "五", "六", "日"]
        if day is None:
            day = to_week
        with open('config.json', encoding="utf-8") as file:
            text = json.load(file)
            self.classes = ["周"] + [week[to_week]] + ["|"] + text["日程表"][str(day + 1)]  # 读取课表
            self.left = text["分隔符"] + ["|"]
            self.selects = text["更换选项"]
            on = text["开始时间"]
            off = text["结束时间"]
            self.times = []
            self.onw = text["开始提示"]
            self.off_w = text["结束提示"]
            self.font = (text["字体"], 40)
            self.speed = text["速度"]
            self.transparency = text["透明度"]
            for x in range(len(on)):
                self.times.append(on[x])
                self.times.append(off[x])

    def create_window(self, is_init=False):
        """
        创建/重置窗口, 将每节课作为label显示
        :param is_init: 默认False,从0创建窗口,若为True则跳过初始化窗口（重绘）
        :return: pass
        """
        # 初始化窗口
        if not is_init:
            self.window = Tk()
            self.window.overrideredirect(True)  # 隐藏标题栏
            self.window.attributes('-topmost', True)  # 置顶
            self.window.attributes('-alpha', self.transparency)  # 窗口透明度
            self.window.config(bg='black')  # 背景色为黑
            self.window.bind('<Double-Button-1>', self.select)  # 绑定按键

        # x 坐标依次显示 label
        position = self.x
        for x in self.classes:
            class_lab = Label(self.window, text=x, font=self.font, fg='white', bg='black', wraplength=40)
            class_lab.place(x=position, y=self.y)
            if x in self.left:
                self.left_labs.append(class_lab)
            else:
                class_lab.x = position  # 为 label 添加 x
                class_lab.num = len(self.left_labs + self.labels)  # 添加 label 所处 classes 位置
                self.labels.append(class_lab)
            position += class_lab.winfo_reqwidth()

            # 设置窗口高度，并且考虑换行情况
            height = class_lab.winfo_reqheight() + self.y * 2
            if height > self.height:
                self.height = height

        self.width = position + self.x  # 设置窗口宽度
        self.root_x = int((self.window.winfo_screenwidth() - self.width) / 2)
        if not is_init:
            self.window.geometry('1x' + str(self.height) + '+' + str(
                int(self.window.winfo_screenwidth() / 2)) + '+' + str(self.root_y))
            self.window.update()
            self.move([self.window], [self.width], [self.height], [self.root_x], [self.root_y])  # 创建窗口

    def select(self, event):
        """
        换课功能
        :param event:
        :return: pass
        """
        self.window.unbind('<Double-Button-1>')
        if event.y_root - self.root_y < self.height:
            a = -1
            for i in self.labels:
                if event.x_root - self.window.winfo_x() >= i.x:
                    a += 1

            if not self.selected:
                if a < 2:  # 选中星期
                    self.labels[0]['bg'] = 'grey'
                    self.labels[1]['bg'] = 'grey'
                    self.select_labs = Label(self.window, text='一 二 三 四 五 六 日 考', font=self.font, fg='white',
                                             bg='black')
                else:
                    self.labels[a]['bg'] = 'grey'
                    self.select_labs = Label(self.window, text=' '.join(self.selects), font=self.font, fg='white',
                                             bg='black')
                self.select_labs.place(x=self.x, y=self.height)
                if self.width < self.select_labs.winfo_reqwidth():
                    self.move([self.window], [self.select_labs.winfo_reqwidth() + self.x * 2],
                              [self.height + self.select_labs.winfo_reqheight() + self.x],
                              [int(self.window.winfo_x() - (self.select_labs.winfo_reqwidth() - self.width) / 2)],
                              [self.root_y], 0.1)
                else:
                    self.move([self.window], [self.width], [self.height + self.select_labs.winfo_reqheight() + self.x],
                              [self.window.winfo_x()], [self.root_y], 0.1)
                self.selected = a
            elif a == self.selected:  # 重复点取消换课
                if a < 2:
                    self.labels[0]['bg'] = 'black'
                    self.labels[1]['bg'] = 'black'
                else:
                    self.labels[a]['bg'] = 'black'
                self.move([self.window], [self.width], [self.height], [self.window.winfo_x()], [self.root_y], 0.1)
                self.select_labs.destroy()
                self.selected = False
            else:
                if self.selected < 2:
                    self.labels[0]['bg'] = 'black'
                    self.labels[1]['bg'] = 'black'
                else:
                    self.labels[self.selected]['bg'] = 'black'
                self.move([self.window], [self.width], [self.height], [self.window.winfo_x()], [self.root_y], 0.1)
                self.select_labs.destroy()

                if a < 2:  # 选中星期
                    self.labels[0]['bg'] = 'grey'
                    self.labels[1]['bg'] = 'grey'
                    self.select_labs = Label(self.window, text='一 二 三 四 五 六 日 考', font=self.font, fg='white',
                                             bg='black')
                else:
                    self.labels[a]['bg'] = 'grey'
                    self.select_labs = Label(self.window, text=' '.join(self.selects), font=self.font, fg='white',
                                             bg='black')
                self.select_labs.place(x=self.x, y=self.height)
                if self.width < self.select_labs.winfo_reqwidth():
                    self.move([self.window], [self.select_labs.winfo_reqwidth() + self.x * 2],
                              [self.height + self.select_labs.winfo_reqheight() + self.x],
                              [int(self.window.winfo_x() - (self.select_labs.winfo_reqwidth() - self.width) / 2)],
                              [self.root_y], 0.1)
                else:
                    self.move([self.window], [self.width], [self.height + self.select_labs.winfo_reqheight() + self.x],
                              [self.window.winfo_x()], [self.root_y], 0.1)
                self.selected = a

        else:
            a = int((event.x_root - self.window.winfo_x() - self.x) / 80)
            if self.selected < 2:
                print(a)
                if a == 8:
                    # 清除整个窗口内容
                    for label in self.labels + self.left_labs:
                        label.destroy()
                    # 显示考试日提示
                    self.move([self.window], [self.x], [self.height], [int(self.window.winfo_screenwidth() / 2)],
                              [self.root_y], 1)
                    exam_label = Label(self.window, text='已设为考试状态，故不提供课表服务', font=self.font, fg='white',
                                       bg='black')
                    exam_label.place(x=self.x, y=self.y)
                    # 清除选择状态
                    self.selected = False
                    self.window.bind('<Double-Button-1>', quit)

                    # 自动调整窗口大小并居中
                    new_width = self.x * 2 + exam_label.winfo_reqwidth()
                    new_height = self.y * 2 + exam_label.winfo_reqheight()
                    new_root_x = int((self.window.winfo_screenwidth() - new_width) / 2)
                    self.move([self.window], [new_width], [new_height], [new_root_x], [self.root_y], 1)
                    self.stop_update = True
                    return
                if a > 6:
                    a = 6
                """重新设置课表"""
                self.load_config(a)
                for x in self.left_labs + self.labels:
                    x.destroy()
                self.left_labs = []
                self.labels = []
                # x 坐标依次显示 label
                self.height = 0
                self.create_window(is_init=True)
                self.now_class = -1
            else:
                if a > len(self.selects) - 1:
                    a = len(self.selects) - 1
                self.labels[self.selected]['bg'] = 'black'
                self.labels[self.selected]['text'] = self.selects[a]
                self.classes[self.labels[self.selected].num] = self.selects[a]

            self.move([self.window], [self.width], [self.height], [self.window.winfo_x()], [self.root_y], 0.1)
            self.select_labs.destroy()
            self.selected = False

        self.window.bind('<Double-Button-1>', self.select)

    def on_class_animation(self):
        """
        上课
        :return: pass
        """
        if self.times[0] == [datetime.now().hour, datetime.now().minute]:
            self.window.unbind('<Double-Button-1>')
            sleep(1)
            xe = self.labels[self.now_class + 2].x
            on_cl = Label(self.window, text=self.labels[self.now_class + 2]['text'], font=self.font, fg='yellow',
                         bg='black', wraplength=40)  # 先行创建上方 label
            if self.off_tk:
                self.move([self.window, self.off_tk[0]], [self.width, 1],
                          [self.height, self.y * 2 + self.off_tk[1].winfo_reqheight()],
                          [self.root_x, int((self.window.winfo_screenwidth() + self.width) / 2) - self.x + 20],
                          [self.root_y, self.root_y])

            # 删除原有
            for i in self.labels + self.left_labs:
                i.destroy()
            try:
                self.select_labs.destroy()
            except AttributeError:
                pass
            if self.off_tk:
                self.off_tk[1].destroy()
                self.off_tk[0].destroy()

            # 缩至一格
            self.move([self.window], [self.x * 2 + on_cl.winfo_reqwidth()], [self.y * 2 + on_cl.winfo_reqheight()],
                      [self.root_x + xe], [self.root_y])
            # 居中放置
            on_cl.place(y=self.y, relx=0.5, anchor='n')
            self.window.update()
            sleep(1)
            # 第二动画
            on_lab = Label(self.window, text=self.onw, font=self.font, fg='yellow', bg='black')
            on_lab.place(relx=0.5, anchor='n', y=self.window.winfo_height())
            self.move([self.window], [self.x * 2 + on_lab.winfo_reqwidth()],
                      [self.y * 3 + on_cl.winfo_reqheight() + on_lab.winfo_reqheight()],
                      [self.root_x + xe - (on_lab.winfo_reqwidth() / 2)], [self.root_y])
            sleep(5)
            # 恢复动画
            self.move([self.window], [self.x * 2 + on_cl.winfo_reqwidth()], [self.y * 2 + on_cl.winfo_reqheight()],
                      [self.root_x + xe], [self.root_y])
            on_cl.destroy()
            on_lab.destroy()
            self.window.update()
            self.move([self.window], [self.width], [self.height], [self.root_x], [self.root_y])

            # x 坐标依次显示 label
            self.left_labs = []
            self.labels = []
            self.x_list = []
            position = self.x
            for x in self.classes:
                class_lab = Label(self.window, text=x, font=self.font, fg='white', bg='black', wraplength=40)
                class_lab.place(x=position, y=self.y)
                if x in self.left:
                    self.left_labs.append(class_lab)
                else:
                    class_lab.x = position  # 为 label 添加 x
                    class_lab.num = len(self.left_labs + self.labels)  # 添加 label 所处 classes 位置
                    self.labels.append(class_lab)
                position += class_lab.winfo_reqwidth()
            self.window.bind('<Double-Button-1>', self.select)

        self.labels[self.now_class + 1]['fg'] = 'white'
        self.labels[self.now_class + 2]['fg'] = 'yellow'
        del (self.times[0])
        self.window.attributes('-topmost', False)

    def off_class_animation(self):
        """
        下课动画
        :return:
        """
        if self.times[0] == [datetime.now().hour, datetime.now().minute]:
            self.window.unbind('<Double-Button-1>')
            sleep(0.5)

            self.off_tk = [None, None]

            temp = self.classes[3:]
            cnt = 0
            cnt2 = self.now_class + 1
            for i in range(len(temp)):
                if cnt2 == 0:
                    break
                if temp[i] != "!":
                    cnt2 -= 1
                if temp[i] == "|":
                    cnt += 1

            # 检查两个连续 "|" 的条件
            if len(self.times) > 1 and temp[self.now_class + 1 + cnt] == "|" and temp[self.now_class + 2 + cnt] == "|":
                # 如果条件满足，将 "午饭" 添加到下课消息
                off_message = "午饭时间"
            elif len(self.times) == 1:
                # 如果是当天的最后一节课，显示 "放学了"
                off_message = "放学了"
            else:
                # 否则，显示常规下课消息
                off_message = self.off_w

            # 创建下课通知窗口
            self.off_tk[0] = Tk()
            self.off_tk[1] = Label(self.off_tk[0], text=off_message, font=self.font, fg='yellow', bg='black')
            self.off_tk[0].overrideredirect(True)
            self.off_tk[0].attributes('-topmost', True)
            self.off_tk[0].attributes('-alpha', 0.7)
            self.off_tk[0].config(bg='black')

            # 定位通知窗口
            self.off_tk[0].geometry('1x' + str(self.y * 2 + self.off_tk[1].winfo_reqheight()) + '+' +
                                    str(int((self.window.winfo_screenwidth() + self.width) / 2) - self.x + 20) + '+' +
                                    str(self.root_y))
            self.off_tk[1].place(x=self.x, y=self.y)
            self.off_tk[0].update()

            # 执行平滑动画
            self.move([self.window, self.off_tk[0]],
                      [self.width, self.x * 2 + self.off_tk[1].winfo_reqwidth()],
                      [self.height, self.y * 2 + self.off_tk[1].winfo_reqheight()],
                      [int((self.window.winfo_screenwidth() - self.width - self.x * 2 - self.off_tk[
                          1].winfo_reqwidth() - 40) / 2),
                       int((self.window.winfo_screenwidth() + self.width - self.off_tk[
                           1].winfo_reqwidth()) / 2) + 20 - self.x],
                      [self.root_y, self.root_y])

            try:
                self.select_labs.destroy()
            except AttributeError:
                pass
            self.window.bind('<Double-Button-1>', self.select)

        self.window.attributes('-topmost', True)
        if len(self.times) == 1:
            self.window.mainloop()
        del (self.times[0])
        self.now_class += 1
        self.labels[self.now_class + 1]['fg'] = 'white'
        self.labels[self.now_class + 2]['fg'] = 'yellow'
        if self.speed < 1:
            sleep(0.1 * (1 / self.speed))

    def find(self):
        """
        程序主要逻辑部分
        :return:
        """
        if not self.times:
            self.window.mainloop()
            self.window.unbind('<Double-Button-1>')
        else:
            if self.times[0][0] < datetime.now().hour:
                if self.status:
                    self.off_class_animation()
                    self.status = False
                else:
                    self.on_class_animation()
                    self.status = True
            elif self.times[0][1] <= datetime.now().minute and self.times[0][0] == datetime.now().hour:
                if self.status:
                    self.off_class_animation()
                    self.status = False
                else:
                    self.on_class_animation()
                    self.status = True
        self.window.update()
        sleep(0.1)


def main():
    cl = Calendar()
    cl.load_config()
    cl.create_window()
    while True:
        if not cl.stop_update:
            cl.find()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
        messagebox.showwarning('error',
                               '程序出错，排查config后若仍出现问题，请把时间、配置文件、程序版本提交至issues上以解决问题')

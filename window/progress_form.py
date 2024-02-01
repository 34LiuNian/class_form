import time
import tkinter


class ProgressForm(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.attributes('-alpha', 1)
        # self.config(bg='#008CFF')
        self.config(bg="#6667AB")
        self.geometry("3000x2+0+0")
        self.update_progress(0)

    def update_progress(self, progress):
        """
        Updates the
        :param progress: 进度百分比
        :return: pass
        """
        screen_width = self.winfo_screenwidth()
        self.geometry("{}x2+0+0".format(int(screen_width * progress / 100)))
        self.update()


if __name__ == '__main__':
    progress_form = ProgressForm()
    for i in range(1, 101):
        progress_form.update_progress(i)
        time.sleep(0.1)


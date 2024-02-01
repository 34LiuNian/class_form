import tkinter


class ProgressForm(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.attributes('-alpha', 0.6)
        # self.config(bg='#008CFF')
        self.config(bg="#6667AB")
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        window_w = int(screen_w * 0.3)
        window_h = int(screen_h * 0.3)
        self.geometry("{}x{}+{}+{}".format(window_w, window_h, int((screen_w - window_w) / 2), int((screen_h - window_h) / 2)))


if __name__ == '__main__':
    progress_form = ProgressForm()
    progress_form.mainloop()
    
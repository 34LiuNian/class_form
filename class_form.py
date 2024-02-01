from window import main_form
from window import progress_form
from tkinter import messagebox


def main():
    cl = main_form.Calendar()
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

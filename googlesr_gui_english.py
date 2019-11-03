from tkinter import Tk, Label, StringVar, OptionMenu, \
                    Button, LEFT, filedialog, IntVar, \
                    Checkbutton
from os import system, getcwd

LANG_CODE_DICT = {u"中文(繁體)": "zh-tw", 
                  u"中文(简体)": "zh-cn",
                  u"English"   : "en", 
                  u"日本語"    : "ja"}

def convert_lang(lang_code):
    return LANG_CODE_DICT[lang_code]
    
def execute():
    if file_name.get() == '' or file_name.get() == u'Select API key!':
        file_name.set(u'Select API key!')
        file_name_label.config(fg="red")
    else:
        lang = convert_lang(lang_code.get())
        cmd_string = 'start cmd /c "set GOOGLE_APPLICATION_CREDENTIALS=%s'%file_name.get() + \
                     ' & googlesr.exe'
        cmd_string += " --lang_code=%s"%lang
        if debug_int.get() == 1:
            cmd_string += " --debug"
        if connect_int.get() == 1:
            cmd_string += " --connect"
        
        cmd_string+='"' # to terminate the command
        system(cmd_string)
    
def choose_file():
    file_name.set('')
    file_name_label.config(fg="black")
    file_name_ = filedialog.askopenfilename(initialdir = getcwd(), 
                                            title = "Select API key", 
                                            filetypes = (("json files","*.json"),("all files","*.*")))
    file_name.set(file_name_)

root = Tk()
root.title(u"Auto Speech2Text")
root.geometry("300x240+200+200")
root.resizable(False, False)

lang_label = Label(text=u'Select audio language')
# lang_label.config(font=("Courier", 12))
lang_label.place(x=30, y=20)
lang_code = StringVar(root)
lang_code.set(u"中文(繁體)")
lang = OptionMenu(root, lang_code, *LANG_CODE_DICT.keys())
# lang.config(font=("Courier", 12), width=8)
lang.place(x=20, y=50)

file_button = Button(text=u'Select API key', command=choose_file)
# file_button.config(font=("Courier", 12))
file_button.place(x=24, y=110)
file_name = StringVar()
file_name.set('')
file_name_label = Label(root, textvariable=file_name, 
                           justify=LEFT, wraplengt=250)
file_name_label.place(x=20, y=150)

connect_int = IntVar()
connect_check = Checkbutton(root, text=u"connect to unity\n(port 5067)", 
                            variable=connect_int,
                            onvalue=1, offvalue=0)
# connect_check.config(font=("Courier", 12))
connect_check.place(x=160, y=5)

debug_int = IntVar()
debug_check = Checkbutton(root, text=u"Display in console", 
                            variable=debug_int,
                            onvalue=1, offvalue=0)
# debug_check.config(font=("Courier", 12))
debug_check.place(x=160, y=50)

file_button = Button(text=u'Start', command=execute)
file_button.config(font=("Courier", 25))
file_button.place(x=160, y=80)

root.mainloop()
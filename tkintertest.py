# import Tkinter as tk # Python 2
import tkinter as tk # Python 3
root = tk.Tk()
# The image must be stored to Tk or it will be garbage collected.
root.image = tk.PhotoImage(file='startup.gif')
label = tk.Label(root, image=root.image, bg='white')
root.overrideredirect(True)
root.geometry("+850+250")
# root.lift()

T = tk.Text(root, height=2, width=40, fg='yellow')
T.pack()
T.insert(tk.END, "Just a text Widget\nin two lines\n")

# root.wm_attributes("-topmost", True)
# root.wm_attributes("-disabled", True)
# root.wm_attributes("-transparentcolor", "white")
# label.pack()
# label.mainloop()

T.pack()
T.insert(tk.END, "Just a text Widget\nin two lines\n")
tk.mainloop()

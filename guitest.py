from tkinter import *

master = Tk()
master.title("FAA Airport Diagram")
Label(master, text='Airport ICAO Code').grid(row=0) 
getBtn = Button(master, text='Download').grid(row=1)
e1 = Entry(master) 
e1.grid(row=0, column=1) 
mainloop()
from tkinter import *
from tkinter import ttk

root = Tk()

# create top level
# create the toplevel to house everything
# dimensions of parent window
x = root.winfo_screenwidth()
y = root.winfo_screenheight()

# set the width to the width of the
repairPOSfieldsTL = Toplevel()
repairPOSfieldsTL.config(background="#DFE8F6")
repairPOSfieldsTL.geometry('%dx%d+%d+%d' % (500, 500, x / 2 - 250, y / 2 - 250))
repairPOSfieldsTL.columnconfigure((0,1,2), weight=1)
repairPOSfieldsTL.rowconfigure((0), weight=1)
repairPOSfieldsTL.resizable(width=False, height=False)

# master frame to put it all in
frame_main = ttk.Frame(repairPOSfieldsTL)
frame_main.grid(row=0, column=0, sticky=NSEW, columnspan=3)
frame_main.grid_columnconfigure(2, weight=1)
frame_main.grid_rowconfigure(2, weight=1)

# labels not involved in scroll region
# Create the table headers
test1 = ttk.Label(frame_main, text="Attribute errors", font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6")
test1.grid(column=0, row=0, sticky=NSEW, columnspan=3)
test2 = ttk.Label(frame_main, text="Error on row", font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6")
test2.grid(column=0, row=1, sticky=NSEW)
test3 = ttk.Label(frame_main, text="Current Value", font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6")
test3.grid(column=1, row=1, sticky=NSEW)
test4 = ttk.Label(frame_main, text="New Value", font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6")
test4.grid(column=2, row=1, sticky=NSEW)

# add a frame to house everything below
subframe = ttk.Frame(frame_main)
subframe.grid(row=2, column=0, sticky=NSEW, columnspan=3)
subframe.grid(row=2, column=0, sticky=NSEW)
subframe.grid_rowconfigure(0, weight=1)
subframe.grid_columnconfigure(0, weight=1)
subframe.grid_propagate(False)

# add canvas into this frame
canvas = Canvas(subframe)
canvas.grid(column=0, row=0, sticky=NSEW)
canvas.config(background="#DFE8F6", highlightthickness=0)

# add scroll bar
vsb = ttk.Scrollbar(subframe, orient="vertical", command=canvas.yview)
vsb.grid(row=0, column=1, sticky=NS)
canvas.configure(yscrollcommand=vsb.set)

# add frame on the canvas to contain the data
label_frame = ttk.Frame(canvas)
label_frame.grid(row=0, column=0, sticky=NSEW)

canvas.create_window((0, 0), window=label_frame, anchor=NW)

# add data
# Add 9-by-5 buttons to the frame
rows = 5
columns = 3
labels = [[ttk.Label(), ttk.Label(), ttk.Combobox] for j in range(rows)]

for i in range(0, rows):
    labels[i][0] = ttk.Label(label_frame, anchor="center", text="%s" % i, borderwidth=3, relief="flat", background="#DFE8F6", width=17)
    labels[i][0].grid(column=0, row=i, sticky=NSEW)
    labels[i][1] = ttk.Label(label_frame, anchor="center", text="%s" % i, borderwidth=3, relief="flat", background="#DFE8F6", width=19)
    labels[i][1].grid(column=1, row=i, sticky=NSEW)
    labels[i][2] = ttk.Combobox(label_frame)
    labels[i][2].grid(column=2, row=i, sticky=NSEW)


# Update buttons frames idle tasks to let tkinter calculate buttons sizes
label_frame.update()

#first5columns_width = sum([labels[0][j].winfo_width() for j in range(0, columns)])
first5rows_height = sum([labels[i][0].winfo_height() for i in range(0, rows)])
subframe.config(height=first5rows_height, width=canvas.winfo_width())

# add buttons to the bottom
ttk.Button(frame_main, text="Fill All").grid(row=3, column=0, sticky=EW)
ttk.Entry(frame_main).grid(row=3, column=1, sticky=EW)
ttk.Button(frame_main, text="Commit").grid(row=3, column=2, sticky=EW)

# Set the canvas scrolling region
canvas.config(scrollregion=canvas.bbox("all"))

root.mainloop()


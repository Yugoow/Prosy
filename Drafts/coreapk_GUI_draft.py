import tkinter as tk
import tkinter.messagebox as tkmsg
import tkinter.filedialog as tkfld
from tkinter import ttk #for the treeview
import os.path, os, sqlite3, itertools


class MainWindow:
	def __init__(self):
		self.parent = tk.Tk()
		self.parent.title("Title here")
		self.parent.geometry("1200x600")
		self.parent.state('zoomed')
		self.parent.bind("<Configure>", self.resize)
		self.fullScreenState = False
		self.parent.bind("<F11>", self.toggleFullScreen)
		self.parent.bind("<Escape>", self.quitFullScreen)
		self.menuBar(self.parent)
		self.frame(self.parent)
		self.parent.mainloop()

	def toggleFullScreen(self, *event):
		self.fullScreenState = not self.fullScreenState
		self.parent.attributes("-fullscreen", self.fullScreenState)

	def quitFullScreen(self, *event):
		self.fullScreenState = False
		self.parent.attributes("-fullscreen", self.fullScreenState)

	def resize(self,event):
		print("New size is: {}x{}".format(event.width, event.height))

	def frame(self,parent):
		parent.rowconfigure(2, weight=1)
		parent.columnconfigure(1, weight=1)
		self.selection_area = tk.Frame(parent, bg="#CACACA",width=225, relief= "groove", bd=3)
		self.selection_area.grid(column=0,row=0 ,rowspan=3,  sticky="swne")

		self.btn_quit = tk.Button(parent, text="Quit", command=self.quit_app, width=10, justify="center")
		self.btn_quit.grid(column=0, row=2, sticky="s", pady=15)


		self.interaction_area = tk.Frame(parent, bg="#404040")
		self.interaction_area.grid(column=1, rowspan=3,row=0,sticky="swne")

		self.action_area = tk.Frame(parent, bg="white", height=125)
		self.action_area.grid(column=1, row=2, sticky="s", pady=15)
		select_area(self.selection_area)
		act_area(self.action_area, self.interaction_area)

	def quit_app(self):
		if tkmsg.askokcancel("Quit ?","You're gonna leave"):
			self.parent.destroy()
			conn.close()
			os.system("TASKKILL /IM python.exe /F") #stop the repl sublim text


	def menuBar(self,parent):
		self.menu = tk.Menu(parent)
		self.menu_file = tk.Menu(self.menu,tearoff=0)
		self.view_file=tk.Menu(self.menu, tearoff=0)
		self.menu_file.add_command(label="Open", command=self.donothing)
		self.menu_file.add_command(label="Save", command=self.donothing)
		self.view_file.add_command(label="Zoom / Dezoom  F11", command=self.toggleFullScreen)
		self.menu.add_cascade(label="File",menu=self.menu_file)
		self.menu.add_cascade(label="View", menu=self.view_file)
		self.menu.add_command(label="Quit", command=self.quit_app)
		parent.config(menu=self.menu)

	def donothing(self):
		self.filepath = tkfld.askopenfilename(title="Open a database",filetypes=[('database files','.db'),('all files','.*')])


class synch_db:
	def __init__(self):
		global cursor,conn
		try:
			conn = sqlite3.connect('data/note_base.db')
			cursor = conn.cursor()
			cursor.execute('CREATE TABLE blocs(id INTEGER PRIMARY KEY NOT NULL, name VARCHAR(30), semestre VARCHAR(10), year VARCHAR(10));')

			cursor.execute('CREATE TABLE conversion(id INT PRIMARY KEY UNIQUE NOT NULL, denomination CHAR(1), value INT);')

			cursor.execute('CREATE TABLE notes(id INTEGER PRIMARY KEY UNIQUE NOT NULL, id_bloc INT, note CHAR(1), coef INT, FOREIGN KEY (id_bloc) REFERENCES blocs(id));')

			cursor.execute('INSERT INTO conversion(id,denomination,value) VALUES (1,"A",5),(2,"B",4),(3,"C",2),(4,"D",1);')

			conn.commit()
			print("Database successfuly created\n")
		except sqlite3.OperationalError:
			print('Erreur la table existe déjà')
		except Exception as e:
			print("Une erreur à été détéctée")
			conn.rollback()

	def get_idBlock(self, name_block):
		cursor.execute("SELECT id FROM blocs WHERE name=?",(name_block,))
		id_of_bloc=cursor.fetchall()
		return id_of_bloc[0][0]

	def list_return(self):
		list_of_blocks=[]
		cursor.execute("""SELECT name, semestre FROM blocs""")
		rows=cursor.fetchall()
		for row in rows:
			list_of_blocks.append(row)

		return list_of_blocks


	def add_block(self, *args):
		cursor.executemany("INSERT INTO blocs(name,semestre) VALUES (?,?)",*args)
		conn.commit()

	def del_block(self, name):
		id_b=synch_db.get_idBlock("",name)
		try:
			cursor.execute("DELETE FROM notes WHERE id_bloc=?",(id_b,))
			cursor.execute("DELETE FROM blocs WHERE id=?",(id_b,))
			conn.commit()
		except:
			return False
		return True


	def req_note(self, name):
		id_b=synch_db.get_idBlock("", name)
		cursor.execute("SELECT notes.note, notes.id, conversion.value, notes.coef,SUM(notes.coef) OVER() from notes INNER JOIN conversion WHERE notes.note=conversion.denomination and notes.id_bloc=? GROUP BY notes.id",(id_b,))
		rows=cursor.fetchall()
		return rows

	def add_notes(self,name,values):
		id_b=synch_db.get_idBlock('',name)
		var_ins=True
		for value in values:
			try:
		 		cursor.executemany("""
	 				INSERT INTO notes(id_bloc,coef,note) VALUES(?, ?, ?)""",[(id_b,value[1],value[0])])
			except:
				var_ins=False
				break
				
		if var_ins:
			conn.commit()
			return var_ins	
		else:
			conn.rollback()
			return var_ins

	def rename_block(self, oldname, newname):
		try:
			cursor.execute("UPDATE blocs SET name=? WHERE name=?",(newname,oldname,))
			conn.commit()
			return True
		except:
			return False



class select_area:
	def __init__(self,master):
		global selfSelect_area
		selfSelect_area=self
		self.bg='#CACACA'
		self.e_msg= tk.StringVar()
		self.v_msg=tk.StringVar()
		self.sem_y=tk.StringVar()

		self.info_select=tk.Label(master, text="Select or search for a block")		
		self.info_select.grid(row=0, columnspan=2)

		self.tree_view=ttk.Treeview(master)
		self.style = ttk.Style(master)
		self.style.configure('Treeview', rowheight=20)
		self.ysb = ttk.Scrollbar(master, orient='vertical', command=self.tree_view.yview)
		self.tree_view.configure(yscroll=self.ysb.set)

		self.tree_view["columns"]=("child_notes")
		self.tree_view.column("#0", minwidth=50, width=150)
		self.tree_view.column("child_notes", minwidth=40, width=50, anchor="n")
		self.tree_view.heading("#0", text='Blocks')
		self.tree_view.heading("child_notes", text='Notes')
		self.tree_view.grid(column=1, row=1)
		self.ysb.grid(column=2, row=1, sticky='ns')

		self.search_label=tk.Label(master, text="Search for a block :", bg=self.bg)
		self.search_label.grid(columnspan=2, row=2)

		self.input_name = tk.Entry(master, bd=2, relief="groove", font=("helvetica",10), justify="center")
		self.input_name.grid(columnspan=2, row=3)
		self.input_name.bind('<Return>',self.search_block)

		self.search_but = tk.Button(master, text="Search", command=self.search_block)
		self.search_but.grid(columnspan=2, row=4)

		self.info_e_msg = tk.Label(master, textvariable=self.e_msg, fg="red", bg=self.bg, font=('helvetica','10'))
		self.info_e_msg.grid(columnspan=2, row=5)

		self.info_v_msg=tk.Label(master, textvariable=self.v_msg, fg="green", bg=self.bg, font=('helvetica','10'))
		self.info_v_msg.grid(columnspan=2, row=6)

		self.treeview()

		self.validation_frame =tk.LabelFrame(master,text="Creation of the block", bg=self.bg, font=("helvetica","11"))

		self.select_cycle = tk.Label(self.validation_frame, text="Choose the cycle :", bg=self.bg)
		self.select_cycle.pack(fill="x")
		self.radiob_1=tk.Radiobutton(self.validation_frame, text="Year 1 - Semester 1", variable=self.sem_y, value='_y1_s1', bg=self.bg)
		self.radiob_2=tk.Radiobutton(self.validation_frame, text="Year 1 - Semester 2", variable=self.sem_y, value='_y1_s2', bg=self.bg)
		self.radiob_1.pack(anchor="w")
		self.radiob_2.pack(anchor="w")


		self.btn_validat=tk.Button(self.validation_frame,text="Create", command=self.add_block)
		self.btn_validat.pack()

	def synch_treeview(self):
		for sem in self.cycle_sem:
			c_sem=len(self.tree_view.get_children(sem))

			self.tree_view.set(sem, column='child_notes', value=c_sem if c_sem!= 0 else "-")
		for y in self.cycle_year:
			c_year=len(self.tree_view.get_children(y[0]+self.s1))+len(self.tree_view.get_children(y[0]+self.s2))

			self.tree_view.set(y[0], column='child_notes', value=c_year if c_year!=0 else "-" )


	def update_subtree(self, *event):
		global iid
		iid = self.tree_view.focus()
		turn=act_area.recup_iid("")

	def tree_delete(self):
		selfSelect_area.tree_view.delete(iid)		

	def treeview(self):
		self.cycle_sem=[]
		self.y1='_y1' #simulation sortie de requête
		self.y2='_y2'
		self.y3='_y3'
		self.y4='_y4'
		self.y5='_y5'

		self.s1='_s1'
		self.s2='_s2'

		#First level (Year)
		self.year1=self.tree_view.insert('','1',self.y1,text='A1', tags='A')
		self.year2=self.tree_view.insert('','2',self.y2,text='A2', tags='A')
		self.year3=self.tree_view.insert('','3',self.y3,text='A3', tags='A')
		self.year4=self.tree_view.insert('','4',self.y4,text='A4', tags='A')
		self.year5=self.tree_view.insert('','5',self.y5,text='A5', tags='A')

		self.cycle_year=[(self.y1,self.year1),(self.y2,self.year2),(self.y3,self.year3),(self.y4,self.year4),(self.y5,self.year5)]
		#Second level (Semester)
		for y in self.cycle_year:
			#self.cycle_sem.append(y[0]) #for childs only in years but it will be 2 (the semesters)
			self.cycle_sem.append(y[0]+self.s1)
			self.cycle_sem.append(y[0]+self.s2)
			self.tree_view.insert(y[1],'end',y[0]+self.s1,text='1st Semester', tags='S')
			self.tree_view.insert(y[1],'end',y[0]+self.s2,text='2nd Semester', tags='S')

		self.tree_view.bind("<<TreeviewSelect>>", self.update_subtree)

		self.tree_view.see(self.y1+self.s1) #Show semesters

		self.db_research()
		self.tree_view.tag_configure('A', font='Arial 10 underline')
		self.tree_view.tag_configure('S', font='helvetica 10 bold')
		#synch_db()

	def db_research(self):
		self.block_list=synch_db.list_return("")

		if self.block_list:
			for block in self.block_list:
				try:
					self.tree_view.insert(block[1], 'end',block[0]+block[1], text=block[0])
				except Exception as e:
					self.e_msg.set("Please restart the app an error occured")

		self.synch_treeview()
		

	def confirmation_area(self):
		self.validation_frame.grid(columnspan=2, row=7)

	def add_block(self):
		self.entry_value=str(self.input_name.get())
		sem_y=self.sem_y.get()
		if sem_y:
			try:
				synch_db.add_block("",[(self.entry_value,sem_y)])
				self.tree_view.insert(sem_y,'end',self.entry_value+sem_y, text=self.entry_value)
				self.validation_frame.grid_forget()
				self.work_on(self.entry_value+sem_y)
				self.e_msg.set("")
				self.v_msg.set("Block "+ self.entry_value+" created")
				self.synch_treeview()
			except:
				self.e_msg.set("Oops this block already exist it seems")
		else:
			self.e_msg.set("The block can't be added")


	def search_block(self, *event):
		self.v_msg.set("")
		vari=False
		self.entry_value = str(self.input_name.get())
		if self.entry_value and self.entry_value != "":
			for self.vald in self.block_list:
				if self.vald[0]==self.entry_value:
					self.blub=self.vald[1]
					self.v_msg.set("Block "+self.entry_value+" found")
					self.e_msg.set("")
					self.validation_frame.grid_forget()
					self.work_on(self.entry_value+self.blub)
					vari=True
			if vari==False:
				self.e_msg.set(self.entry_value+" doesn't exist")
				self.confirmation_area()
		else:
			self.e_msg.set("Oops, the entry is empty\nPlease retry")


	def work_on(self, idds):
		self.tree_view.selection_set(idds)
		self.tree_view.focus(idds)
		self.tree_view.see(idds)

	def rename_this_block(self, newname):
		global iid, block_name
		self.tree_view.delete(iid)
		self.tree_view.insert(cycle_in,'end',newname+cycle_in, text=newname)
		self.work_on(newname+cycle_in)


class act_area:
	def __init__(self, master_act, master_interact):
		global Name, block_name
		block_name = ''
		Name=tk.StringVar()
		self.bg='#404040'
		self.info_var=tk.StringVar()

		#Frames des actions
		self.add =tk.LabelFrame(master_interact, bg=self.bg, text="Add", fg="white")
		self.view =tk.LabelFrame(master_interact, bg=self.bg, text="View", fg="white")
		self.avg =tk.LabelFrame(self.view,bg=self.bg,text="Average", fg="white")
		self.sim =tk.LabelFrame(master_interact, bg=self.bg, text="Simulation", fg="white")

		self.info_action=tk.Label(master_act,text="Select an action :")
		self.info_action.grid(column=0, row=0, columnspan=2)

		self.add_notes=tk.Button(master_act,padx=5,pady=2, text="Add", command=lambda:self.pack_frame(self.add,0))
		self.add_notes.grid(column=1, row=1,padx=15, pady=15)
		
		self.view_notes = tk.Button(master_act,padx=5,pady=2, text="View", command=lambda:self.pack_frame(self.view,2))
		self.view_notes.grid(column=2, row=1,padx=15, pady=15)
		
		self.avg_notes=tk.Button(master_act,padx=5,pady=2, text="Average", command=lambda:self.pack_frame('',3))
		
		self.simulation_notes = tk.Button(master_act,padx=5,pady=2, text="Simulation", command=lambda:self.pack_frame(self.sim,1))
		self.simulation_notes.grid(column=4, row=1,padx=15, pady=15)

		self.rename_block = tk.Button(master_act,padx=5,pady=2, text="Rename", command=lambda:self.pack_frame("",4))
		self.rename_block.grid(column=5, row=1,padx=15, pady=15)
		
		self.delete_block=tk.Button(master_act,padx=5,pady=2, text="Delete", command=lambda:self.pack_frame('',9))
		self.delete_block.grid(column=6, row=1,padx=15, pady=15)

		self.info_msg=tk.Label(master_act, textvariable=self.info_var,bg="white", fg="blue")
		self.info_msg.grid(row=2,columnspan=15,column=0,padx=20, pady=5, sticky="e")


		self.block_title=tk.Label(master_interact, bg=self.bg, textvariable=Name, fg="white", font=('helvetica','12'))
		self.block_title.pack()


		#######################


		self.nbr_entry = tk.Spinbox(self.add, from_=1, to=25, width=10)
		self.nbr_entry.grid(column=0,row=0,padx=5)
		self.nbr_entry.bind('<Return>',self.pos_entry_widget)

		self.incr_note_area=tk.Button(self.add, text="+", command=self.pos_entry_widget)
		self.incr_note_area.grid(column=1,row=0)
		self.but_add = tk.Button(self.add, text="Add",font=('helvetica',9), command=self.get_entry_adding)

		self.output_notes = tk.Text(self.view, bg=self.bg, fg="white", bd=0)
		self.output_notes.pack(fill="both", side=tk.LEFT)
		self.average_lbl = tk.Text(self.avg, relief="groove", bg="#5F9EA0", fg="white", height=5)
		self.average_lbl.pack(fill="both")


		self.yscb_act = tk.Scrollbar(self.view, orient='vertical', command=self.output_notes.yview)
		self.output_notes.configure(yscrollcommand=self.yscb_act)
		self.yscb_act.pack(fill="y", side="right")


		self.nb_sim = tk.Spinbox(self.sim, from_=1, to=4, width=10)
		self.nb_sim.grid(column=0,row=0,padx=5)
		self.nb_sim.bind('<Return>',self.simulation_zone)

		self.incr_sim=tk.Button(self.sim, text="+", command=self.simulation_zone)
		self.incr_sim.grid(column=1,row=0)
		self.but_sim = tk.Button(self.sim, text="Simulate",font=('helvetica',9), command=self.get_entry_sim)
		self.output_simulation = tk.Text(self.sim, bg=self.bg, fg="white", bd=0)




	def simulation_zone(self, *event):
		self.combo_name_sim={}
		self.combo_widg_sim=[]
		self.var_coeff="coeffEntry_insim_"
		self.iterat_sim=int(self.nb_sim.get())

		if self.iterat_sim>10:
			self.info_var.set(str(self.iterat_sim)+" is too much, please choose a number less than (or equal to) 10")
		elif self.iterat_sim<=10:
			self.info_var.set("")
			self.but_sim.grid(column=1,columnspan=2,row=99)
			self.coeff_lab_sim=tk.Label(self.sim, text="Coefficient",bg=self.bg, fg="white")
			self.coeff_lab_sim.grid(column=2, row=1)
			pos=2

			for i in range(1,self.iterat_sim+1):
				self.combo_name_sim["N°"+str(i)]=self.var_coeff+str(i)

			for numb, coeff in self.combo_name_sim.items():
				numb=tk.Label(self.sim, text=numb, bg=self.bg, fg="white")
				numb.grid(column=0, pady=2,row=pos)

				coeff=tk.Spinbox(self.sim, from_=1, to=10,wrap=True,width=5)
				coeff.grid(column=2,row=pos)
				self.combo_widg_sim.append((coeff, numb))
				pos+=1

		else:
			self.info_var.set("Wrong entry, please retry")

	def get_entry_sim(self):
		global text_sim
		self.simulation_coeff=[]
		text_sim=[]
		self.info_var.set("Loading the simulation, please wait")
		for input_inSim in self.combo_widg_sim:
			coeff_inSim=int(input_inSim[0].get())

			if coeff_inSim:
				self.simulation_coeff.append(coeff_inSim)

		text_sim.append("Coeff : "+str(self.simulation_coeff)+"\n")
		self.output_simulation.grid(column=4,row=1, sticky="ns")
		self.yscb_sim = tk.Scrollbar(self.sim, orient='vertical', command=self.output_simulation.yview)
		self.output_simulation.configure(yscrollcommand=self.yscb_sim)
		self.yscb_sim.grid(column=10, row=1, sticky="nse")

		self.sim_n()

			
		self.but_sim.grid_forget()
		self.coeff_lab_sim.grid_forget()


		for inputs in self.combo_widg_sim:
			inputs[0].grid_forget()
			inputs[1].grid_forget()



	def sim_n(self):
		global text_sim
		stor=self.avg_n(self.show_n())
		coeff_lft=0
		coeff_uni=[]
		self.output_simulation.config(state="normal")
		self.output_simulation.delete("1.0","end")

		for coeff in self.simulation_coeff:
			coeff_lft+=int(coeff)
			coeff_uni.append(int(coeff))


		all_comb=list(itertools.product("5421", repeat=self.iterat_sim)) #All combinaisons

		list_fin_A=[]
		list_note_A=[]
		list_fin_B=[]
		list_note_B=[]
		
		for w in range(len(all_comb)):
			tot_inlist=0
			for j in range(self.iterat_sim):
				tot_inlist+=int(all_comb[w][j])*coeff_uni[j]

			moy_new=(tot_note+tot_inlist)/(tot_val+coeff_lft)
			if moy_new>=3.6 and moy_new<4.6:
				list_fin_B.append(all_comb[w])

			if moy_new>=4.6:
				list_fin_A.append(all_comb[w])


		text_sim.append("\nTo B :")

		if not list_fin_B:
			text_sim.append("\nImpossible to get B with this number of notes...")
		else:
			for ibis in range(len(list_fin_B)):
				buffe=[]
				for jibis in range(self.iterat_sim):
					if list_fin_B[ibis][jibis] == "5":
						buffe.append("A")
					elif list_fin_B[ibis][jibis] == "4":
						buffe.append("B")
					elif list_fin_B[ibis][jibis] == "2":
						buffe.append("C")
					elif list_fin_B[ibis][jibis] == "1":
						buffe.append("D")
				list_note_B.append(buffe)
			for a in range(1,len(list_note_B)+1):
				text_sim.append("\nCombinaison "+str(a)+" : {0} | (coeff {1})".format(list_note_B[a-1], coeff_uni))

		text_sim.append("\n\nTo A :")
		if not list_fin_A:
			text_sim.append("\nImpossible to get A with this number of notes...")
		else:
			for ibis in range(len(list_fin_A)):
				buffe=[]
				for jibis in range(self.iterat_sim):
					if list_fin_A[ibis][jibis] == "5":
						buffe.append("A")
					elif list_fin_A[ibis][jibis] == "4":
						buffe.append("B")
					elif list_fin_A[ibis][jibis] == "2":
						buffe.append("C")
					elif list_fin_A[ibis][jibis] == "1":
						buffe.append("D")
				list_note_A.append(buffe)
			for a in range(1,len(list_note_A)+1):
				text_sim.append("\nCombinaison "+str(a)+" : {0} | (coeff {1})".format(list_note_A[a-1], coeff_uni))
				
		self.output_simulation.insert("end", ''.join(text_sim))
		self.output_simulation.config(state="disabled")



	def pos_entry_widget(self, *event):					#finir cette partie de add entry
		self.combo_name_add={}
		self.combo_widg_add=[]
		self.order_notes=[]
		self.label_pos={}
		self.list_notes=["A","B", "C","D"]
		self.var_entry="combEntry_inadd_"
		self.var_coeff="coeffEntry_inadd_"
		self.iterat_add=int(self.nbr_entry.get())
		self.but_add.grid(column=1,columnspan=2,row=99)
		self.note_lab=tk.Label(self.add, text="Note", bg=self.bg, fg="white")
		self.note_lab.grid(column=1, row=1)
		self.coeff_lab=tk.Label(self.add, text="Coefficient",bg=self.bg, fg="white")
		self.coeff_lab.grid(column=3, row=1)
		pos=2

		for i in range(1,self.iterat_add+1):
			self.combo_name_add[self.var_entry+str(i)]=self.var_coeff+str(i)
			self.label_pos[str(i+1)]="N°"+str(i)

		for entry, coeff in self.combo_name_add.items():
			entry=ttk.Combobox(self.add, values=self.list_notes, state='readonly',width=5)
			entry.grid(column=1,columnspan=2,row=pos, pady=10, padx=10)
			coeff=tk.Spinbox(self.add, from_=1, to=10,wrap=True,width=5)
			coeff.grid(column=3,row=pos)
			self.combo_widg_add.append((entry,coeff))
			pos+=1

		for key,val in self.label_pos.items():
			val=tk.Label(self.add, text=val, bg=self.bg, fg="white")
			val.grid(column=0, row=key)
			self.order_notes.append(val)


	def get_entry_adding(self):
		input_value=[]
		for inputs in self.combo_widg_add:
			char_inputs=inputs[0].get()
			coeff_inputs=int(inputs[1].get())

			if char_inputs and coeff_inputs:
				input_value.append((char_inputs,coeff_inputs))

		self.add_n(input_value)

		self.but_add.grid_forget()
		self.note_lab.grid_forget()
		self.coeff_lab.grid_forget()
		for inputs in self.combo_widg_add:
			inputs[0].grid_forget()
			inputs[1].grid_forget()

		for val in self.order_notes:
			val.grid_forget()



	def view_set(self):
		self.avg.pack_forget()
		rows=self.show_n()
		self.output_notes.config(state="normal")
		self.output_notes.delete("1.0","end")
		if rows:
			for row in rows:
				text="Note :  {0}  |Coefficient :  {2}   |Valeur :  {1}\n".format(row[0],row[2],row[3])
				self.output_notes.insert("end", text)
		else:
			self.output_notes.insert("end","This block is empty")
		self.avg_notes.grid(column=3, row=1,padx=15, pady=15)
		self.output_notes.config(state="disabled")

	def avg_set(self):
		self.average_lbl.config(state="normal")
		avg_txt=self.avg_n(self.show_n())

		self.avg.pack(side=tk.RIGHT, anchor="n")
		self.average_lbl.delete("1.0","end")
		self.average_lbl.insert("end", avg_txt)
		self.average_lbl.config(state="disabled")
		

	def show_n(self):
		rows=synch_db.req_note("", block_name)
		return rows


	def avg_n(self, rows):
		global tot_note, tot_val
		if not rows:
			return "This block is empty"

		tot_note=0
		tot_val=rows[0][4]

		for row in rows:
			tot_note += (row[2]*row[3])
		avg = tot_note/tot_val
		if avg>=3.6 and avg<4.6:
			note_avg="B"
		elif avg>=4.6:
			note_avg="A"
		elif avg<3.6 :
			note_avg="not validated"
		output="Your current average is : "+str(avg)+"\nYour score in this block is "+str(note_avg)+"\n"
		return output


	def add_n(self,list_notation):
		out=synch_db.add_notes('',block_name,list_notation)
		if out:
			self.info_var.set('All notes have been added')	
		else:
			self.info_var.set("The notes can't be added")


	def pack_frame(self,widget,act,*arg):
		if not block_name:
			tkmsg.showwarning("Select a block","No block selected, please choose one")
		elif block_name and act==9:
			self.delete_ablock()

		elif act==3:
			self.avg_set()
		elif act==4:
			self.rename_it()
		else:
			self.add.pack_forget()
			self.avg_notes.grid_forget()
			self.view.pack_forget() #Why not a list of all the frame in a for boucle to unpack
			self.sim.pack_forget()
			widget.pack(fill="both", expand=1)
			if act==2:self.view_set()
			elif act==1:self.nb_sim.focus_set() 


	def delete_ablock(self):
		global iid
		if tkmsg.askyesno("Delete","Do you really want to delete "+block_name+" ?"):
			if synch_db.del_block("",block_name):
				select_area.tree_delete("")
				select_area.synch_treeview(selfSelect_area)
				self.info_var.set(block_name+" succesfully deleted !")
				Name.set("")
				iid=""
			else:
				self.info_var.set("Something went wrong...")

	def rename_it(self):
		self.error_msg=tk.StringVar()
		self.tp_rename=tk.Toplevel()
		self.tp_rename.title("Rename")
		self.tp_rename.geometry("200x150")
		self.lab_tp=tk.Label(self.tp_rename, text="New name :")
		self.lab_tp.pack()
		self.ent_tp=tk.Entry(self.tp_rename)
		self.ent_tp.pack()
		self.ent_tp.focus_set()
		self.ent_tp.bind('<Return>',self.rename_val)
		self.but_tp=tk.Button(self.tp_rename,text="Rename", command=self.rename_val)
		self.but_tp.pack()
		self.lab_error=tk.Label(self.tp_rename, textvariable=self.error_msg)
		self.lab_error.pack()

	def rename_val(self,*event):
		global block_name
		self.newname=str(self.ent_tp.get())
		if self.newname and self.newname!='':
			synch_db.rename_block('',block_name,self.newname)
			selfSelect_area.rename_this_block(self.newname)
			self.error_msg.set(block_name+" is now "+self.newname+" !")
			selfSelect_area.update_subtree()
			self.quit_rename=tk.Button(self.tp_rename, text="Close", command=self.tp_rename.destroy)
			self.quit_rename.pack()
		else:
			self.error_msg.set("Please enter Something")

	def recup_iid(self):
		global block_name, cycle_in
		id_spl=iid.split("_")
		cycle_in="_"+id_spl[1]+"_"+id_spl[2]
		if id_spl[0]!='':
			block_name=id_spl[0]
			Name.set("Working on "+block_name)


if not os.path.isdir('data'):
	os.makedirs("data")

# Vérifier si le fichier existe ou non
if os.path.isfile('data/note_base.db'): #Attention se créé différement lorsque on l'execute en bash
    print("Fichier trouvé")
    conn = sqlite3.connect('data/note_base.db')
    cursor = conn.cursor()

else:
	print("Création de la base de donnée")
	synch_db()


if __name__=="__main__":
	MainWindow()

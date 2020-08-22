import tkinter as tk
import tkinter.messagebox as tkmsg
import tkinter.filedialog as tkfld
from tkinter import ttk #for the treeview
import os.path, os, sqlite3, itertools

		#	Blk = block / ttl = title / ety = entry / btn = button / E = Error / S = Success / radb = radiobutton (S1 = semester 1 / S2 = semester 2)
		#   reg = registration (dictionnary or summary) / Ch = childs / Foc= focus / Rnm = Rename / Frm = Frame / Spn = spin (spinbox)


########## Menu bar (=toolbar)

class Toolbar(tk.Menu):
	def __init__(self, parent, *args, **kwargs):
		tk.Menu.__init__(self, parent, *args, **kwargs)
		self.parent=parent
		self.menu_file = tk.Menu(self,tearoff=0)
		self.view_file=tk.Menu(self, tearoff=0)
		self.menu_file.add_command(label="Open", command=self.donothing)
		self.menu_file.add_command(label="Save", command=self.donothing)
		self.add_cascade(label="File", menu=self.menu_file)
		self.add_cascade(label="View", menu=self.view_file)
		self.add_command(label="Quit",command=lambda:quit_app(self.parent))
		self.parent.config(menu=self)


	##### global function from MainWindow class

	def mainWin_cmd(self, *args):
		self.view_file.add_command(label="Zoom / Dezoom (F11)",command=args[0])


	def donothing(self):
		self.filepath = tkfld.askopenfilename(title="Open a database",filetypes=[('database files','.db'),('all files','.*')])


########## Selection bar (=naviguation)

class Navbar(tk.Frame):
	def __init__(self, parent, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.parent=parent
		self.bg="#CACACA"
		self.nMsg_E=tk.StringVar() #Error msg in nav panel
		self.nMsg_S=tk.StringVar() #Success msg in nav panel
		self.navCblk_idCylce=tk.StringVar() # Var for radiobuttons

		self.config(bg=self.bg,width=225, relief= "groove", bd=3)

		### Widgets

			## Title
		self.nav_ttl=tk.Label(self, text="Select or search for a block")		
		self.nav_ttl.grid(row=0, columnspan=2)

			## Treeview (Style / scrollbar)
		self.navTree=ttk.Treeview(self)
		self.navStyle = ttk.Style(self)
		self.navTree_yscrb = ttk.Scrollbar(self, orient='vertical', command=self.navTree.yview) #yscrb = vertical (y) scrollbar

		self.navTree.grid(column=1, row=1)
		self.navTree_yscrb.grid(column=2, row=1, sticky='ns')
		self.set_navTree()

			## Search area
		self.navSearch_ttl=tk.Label(self, text="Search for a block :", bg=self.bg)
		self.navSearch_ttl.grid(columnspan=2, row=2)

		self.navSearch_ety = tk.Entry(self, bd=2, relief="groove", font=("helvetica",10), justify="center")
		self.navSearch_ety.grid(columnspan=2, row=3)
		self.navSearch_ety.bind('<Return>',self.search_navBlk)

		self.navSearch_btn = tk.Button(self, text="Search", command=self.search_navBlk)
		self.navSearch_btn.grid(columnspan=2, row=4)

			## Message area
		self.navMsg_E = tk.Label(self, textvariable=self.nMsg_E, fg="red", bg=self.bg, font=('helvetica','10'))
		self.navMsg_E.grid(columnspan=2, row=5)

		self.navMsg_S=tk.Label(self, textvariable=self.nMsg_S, fg="green", bg=self.bg, font=('helvetica','10'))
		self.navMsg_S.grid(columnspan=2, row=6)



	def set_navTree(self):
		# Style
		self.navStyle.configure('Treeview', rowheight=20)

		# Scrollbar
		self.navTree.configure(yscroll=self.navTree_yscrb.set)

		# Treeview headers
		self.navTree["columns"]=("child_notes")
		self.navTree.column("#0", minwidth=50, width=150)
		self.navTree.column("child_notes", minwidth=40, width=50, anchor="n")
		self.navTree.heading("#0", text='Blocks')
		self.navTree.heading("child_notes", text='Notes')

		# Binding navtree
		self.navTree.bind("<<TreeviewSelect>>", self.get_navtreeFoc)

		#Treeview data
			# regCh is for registration of all childs (Blocks) and so the number of childs
		self.navTree_regCh=[]

			# List of semesters possibles (2 per year but can do 10 semester in total (y1 : 1/2; y2 : 3/4; ...; y5 : 9/10))
		self.id_semesters=['_s1','_s2']

			# List of years (5 by default)
		self.id_years=['_y'+str(i) for i in range(1,6)] #Years


		#Firts level (years)
		self.navTree_yearWidg=[self.navTree.insert('',i,self.id_years[i-1],text='Y'+str(i), tags='A') for i in range(1,6)]
		""" Same as :
		i=0
		for year in self.navTree_yearWidg:
			self.year=self.navTree.insert('','1',self.id_years[i], text="A"+str(i))
			i+=1
		"""

		#Second level (Semester)
		for i in range(len(self.navTree_yearWidg)):
			for j in range(1,len(self.id_semesters)+1):
				self.navTree_regCh.append(self.id_years[i]+self.id_semesters[j-1])
				self.navTree.insert(self.navTree_yearWidg[i],'end',self.id_years[i]+self.id_semesters[j-1],text='Semester '+str(j), tags='S')

		# Tags settings
		self.navTree.tag_configure('A', font='Arial 10 underline')
		self.navTree.tag_configure('S', font='helvetica 10 bold')

		#Show semesters (pre-selection)
		self.navTree.see('_y1_s1')

		# sub-functions
			# Synch with database and sort blocks
		self.import_dbBlk()

			# synch childs in levels
		self.set_navTreeCh()


	# Setting creation block (zone)
	def set_navCblk(self):
		# Frame
		self.navC_blk =tk.LabelFrame(self,text="Creation of the block", bg=self.bg, font=("helvetica","11"))

		# Title
		self.navValid_ttl = tk.Label(self.navC_blk, text="Choose the cycle :", bg=self.bg)
		self.navValid_ttl.pack(fill="x")

		# Radiobuttons
		self.navValid_radbS1=tk.Radiobutton(self.navC_blk, text="Year 1 - Semester 1", variable=self.navCblk_idCylce, value='_y1_s1', bg=self.bg)
		self.navValid_radbS2=tk.Radiobutton(self.navC_blk, text="Year 1 - Semester 2", variable=self.navCblk_idCylce, value='_y1_s2', bg=self.bg)
		self.navValid_radbS1.pack(anchor="w")
		self.navValid_radbS2.pack(anchor="w")

		# Validation button
		self.navValid_btn=tk.Button(self.navC_blk,text="Create", command=self.create_navBlk)
		self.navValid_btn.pack()

		# Frame grid
		self.navC_blk.grid(columnspan=2, row=7)
		


	def import_dbBlk(self):
		self.db_blocks=Db_handling.get_dbBlk_list("")

		if self.db_blocks:
			for block in self.db_blocks:
				try:
					self.navTree.insert(block[1], 'end',block[0]+block[1], text=block[0])
				except Exception as e:
					self.nMsg_E.set("Please restart the app, an error occured")

		self.set_navTreeCh()



	def set_navTreeCh(self):
		# Number of childs in parents
		for reg_childs in self.navTree_regCh:
			ch_number=len(self.navTree.get_children(reg_childs))
			# Tree maj
			self.navTree.set(reg_childs, column='child_notes', value=ch_number if ch_number!= 0 else "-")

		# Number of childs in master's parents
		for y_id in self.id_years:
			ch_numberYear=len(self.navTree.get_children(y_id+self.id_semesters[0]))+len(self.navTree.get_children(y_id+self.id_semesters[1]))
			# Tree maj
			self.navTree.set(y_id, column='child_notes', value=ch_numberYear if ch_numberYear!=0 else "-" )



	def get_navtreeFoc(self, *event):
		global id_foc
		id_foc = self.navTree.focus()
		get_iidBlk()



	def workon_navTree(self, idds):
		# setting the focus on imaginary selection
		self.navTree.selection_set(idds)
		self.navTree.focus(idds)
		self.navTree.see(idds)



	def rename_navTreeBlk(self, newname):
		self.navTree.delete(id_foc)
		self.navTree.insert(cycleIn,'end',newname+cycleIn, text=newname)
		self.workon_navTree(newname+cycleIn)



	def delete_navTreeBlk(self):
		self.navTree.delete(id_foc)



	def search_navBlk(self):
		self.navMsg_S.set("")
		
		# getting entry value
		self.navSearch_value = str(self.navSearch_ety.get())
		
		# Verification var
		ver_Var=False
		
		# if entry value not empty
		if self.navSearch_value and self.navSearch_value != "":

			for self.blk_info in self.db_blocks:

				#if searched block is in db
				if self.navSearch_value==self.blk_info[0]:

					# Getting semester and year value (cycle)
					self.info_cycle=self.blk_info[1]

					#Settings messages
					self.navMsg_S.set("Block "+self.navSearch_value+" found")
					self.navMsg_E.set("")

					# forget nav creation block frame
					self.navC_blk.grid_forget()

					# Setting work on funct
					self.workon_navTree(self.navSearch_value+self.info_cycle)

					# updating verification variable
					ver_Var=True

			# comparing (if ver_var == False then the block searched doesn't exist in the db)
			if ver_Var==False:
				self.navMsg_E.set(self.navSearch_value+" doesn't exist")

				# Showing the frame for create the block
				self.set_navCblk()

		else:
			self.navMsg_E.set("Oops, the entry is empty\nPlease retry")



	def create_navBlk(self):
		# getting entry value
		self.navSearch_value = str(self.navSearch_ety.get())

		navCblk_idCylce=self.navCblk_idCylce.get() 

		#if navCblk_idCylce not empty
		if navCblk_idCylce:
			try:
				# Adding block in db
				Db_handling.add_dbBlk("",[(self.navSearch_value,navCblk_idCylce)])

				# Adding block in treeview
				self.navTree.insert(navCblk_idCylce,'end',self.navSearch_value+navCblk_idCylce, text=self.navSearch_value)

				# forget nav creation block frame
				self.navC_blk.grid_forget()
				
				# Setting work on funct
				self.workon_navTree(self.navSearch_value+navCblk_idCylce)
				
				# Settingd messages
				self.navMsg_E.set("")
				self.navMsg_S.set("Block "+ self.navSearch_value+" created")
				
				# Treeview synch childs
				self.set_navTreeCh()

			except:
				self.navMsg_E.set("Oops this block already exist it seems")
		else:
			self.navMsg_E.set("The block can't be added")



########## Output zone (=Output area)		########TO DO

class Outarea(tk.Frame):
	def __init__(self, parent, *args, **kwargs):
		global out_ttlVal, act_frames

		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.parent=parent
		self.config(bg="#404040")

		out_ttlVal=tk.StringVar()

		self.bg='#404040'


		self.block_title=tk.Label(self, bg=self.bg, textvariable=out_ttlVal, fg="white", font=('helvetica','12'))
		self.block_title.pack()

		# Actions frames
		self.outFrm_add =tk.LabelFrame(self, bg=self.bg, text="Add", fg="white")
		self.outFrm_view =tk.LabelFrame(self, bg=self.bg, text="View", fg="white")
		self.outFrm_Vavg =tk.LabelFrame(self.outFrm_view,bg=self.bg,text="Average", fg="white")
		self.outFrm_sim =tk.LabelFrame(self, bg=self.bg, text="Simulation", fg="white")

		act_frames=[self.outFrm_add,self.outFrm_view,self.outFrm_sim]

		# Add frame
			# Spinbox
		self.outAdd_spn = tk.Spinbox(self.outFrm_add, from_=1, to=25, width=10)
		self.outAdd_spn.grid(column=0,row=0,padx=5)
		self.outAdd_spn.bind('<Return>',self.set_add)

		self.outAdd_btn=tk.Button(self.outFrm_add, text="+", command=self.set_add)
		self.outAdd_btn.grid(column=1,row=0)

			# Validation
		self.outAdd_valid = tk.Button(self.outFrm_add, text="Add",font=('helvetica',9), command=self.get_valAdd)

		# View frame
		self.outView_notes = tk.Text(self.outFrm_view, bg=self.bg, fg="white", bd=0)
		self.outView_notes.pack(fill="both", side=tk.LEFT)
		self.outView_avg = tk.Text(self.outFrm_Vavg, relief="groove", bg="#5F9EA0", fg="white", height=5)
		self.outView_avg.pack(fill="both")

		self.outView_yscrb = tk.Scrollbar(self.outFrm_view, orient='vertical', command=self.outView_notes.yview)
		self.outView_notes.configure(yscrollcommand=self.outView_yscrb)
		self.outView_yscrb.pack(fill="y", side="right")

		# Simulation frame
		self.outSim_spn = tk.Spinbox(self.outFrm_sim, from_=1, to=4, width=10)
		self.outSim_spn.grid(column=0,row=0,padx=5)
		self.outSim_spn.bind('<Return>',self.set_sim)

		self.outSim_btn=tk.Button(self.outFrm_sim, text="+", command=self.set_sim)
		self.outSim_btn.grid(column=1,row=0)
		self.outSim_valid = tk.Button(self.outFrm_sim, text="Simulate",font=('helvetica',9), command=self.get_valSim)
		self.outSim_output = tk.Text(self.outFrm_sim, bg=self.bg, fg="white", bd=0)



	# Setting the simulation area
	def set_sim(self, *event):
		self.combo_name_sim={}
		self.combo_widg_sim=[]
		self.var_coeff="coeffEntry_insim_"
		self.iterat_sim=int(self.outSim_spn.get())

		if self.iterat_sim>10:
			aMsg.set(str(self.iterat_sim)+" is too much, please choose a number less than (or equal to) 10")
		elif self.iterat_sim<=10:
			aMsg.set("")
			self.outSim_valid.grid(column=1,columnspan=2,row=99)
			self.coeff_lab_sim=tk.Label(self.outFrm_sim, text="Coefficient",bg=self.bg, fg="white")
			self.coeff_lab_sim.grid(column=2, row=1)
			pos=2

			for i in range(1,self.iterat_sim+1):
				self.combo_name_sim["N°"+str(i)]=self.var_coeff+str(i)

			for numb, coeff in self.combo_name_sim.items():
				numb=tk.Label(self.outFrm_sim, text=numb, bg=self.bg, fg="white")
				numb.grid(column=0, pady=2,row=pos)

				coeff=tk.Spinbox(self.outFrm_sim, from_=1, to=10,wrap=True,width=5)
				coeff.grid(column=2,row=pos)
				self.combo_widg_sim.append((coeff, numb))
				pos+=1

		else:
			aMsg.set("Wrong entry, please retry")


	# getting entry in the simulation area and start it
	def get_valSim(self):
		global text_sim
		self.simulation_coeff=[]
		text_sim=[]
		aMsg.set("Loading the simulation, please wait")
		for input_inSim in self.combo_widg_sim:
			coeff_inSim=int(input_inSim[0].get())

			if coeff_inSim:
				self.simulation_coeff.append(coeff_inSim)

		text_sim.append("Coeff : "+str(self.simulation_coeff)+"\n")
		self.outSim_output.grid(column=4,row=1, sticky="ns")
		self.yscb_sim = tk.Scrollbar(self.outFrm_sim, orient='vertical', command=self.outSim_output.yview)
		self.outSim_output.configure(yscrollcommand=self.yscb_sim)
		self.yscb_sim.grid(column=10, row=1, sticky="nse")


		# Start the simulation
		self.start_sim()

			
		self.outSim_valid.grid_forget()
		self.coeff_lab_sim.grid_forget()


		for inputs in self.combo_widg_sim:
			inputs[0].grid_forget()
			inputs[1].grid_forget()


	# Starting the simulation
	def start_sim(self):
		global text_sim
		stor=self.avg_n(self.get_valNotes())
		coeff_lft=0
		coeff_uni=[]
		self.outSim_output.config(state="normal")
		self.outSim_output.delete("1.0","end")

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
				
		self.outSim_output.insert("end", ''.join(text_sim))
		self.outSim_output.config(state="disabled")



	def set_add(self, *event):
		self.combo_name_add={}
		self.combo_widg_add=[]
		self.order_notes=[]
		self.label_pos={}
		self.list_notes=["A","B", "C","D"]
		self.var_entry="combEntry_inadd_"
		self.var_coeff="coeffEntry_inadd_"
		self.iterat_add=int(self.outAdd_spn.get())
		self.outAdd_valid.grid(column=1,columnspan=2,row=99)
		self.note_lab=tk.Label(self.outFrm_add, text="Note", bg=self.bg, fg="white")
		self.note_lab.grid(column=1, row=1)
		self.coeff_lab=tk.Label(self.outFrm_add, text="Coefficient",bg=self.bg, fg="white")
		self.coeff_lab.grid(column=3, row=1)
		pos=2

		for i in range(1,self.iterat_add+1):
			self.combo_name_add[self.var_entry+str(i)]=self.var_coeff+str(i)
			self.label_pos[str(i+1)]="N°"+str(i)

		for entry, coeff in self.combo_name_add.items():
			entry=ttk.Combobox(self.outFrm_add, values=self.list_notes, state='readonly',width=5)
			entry.grid(column=1,columnspan=2,row=pos, pady=10, padx=10)
			coeff=tk.Spinbox(self.outFrm_add, from_=1, to=10,wrap=True,width=5)
			coeff.grid(column=3,row=pos)
			self.combo_widg_add.append((entry,coeff))
			pos+=1

		for key,val in self.label_pos.items():
			val=tk.Label(self.outFrm_add, text=val, bg=self.bg, fg="white")
			val.grid(column=0, row=key)
			self.order_notes.append(val)


	def get_valAdd(self):
		input_value=[]
		for inputs in self.combo_widg_add:
			char_inputs=inputs[0].get()
			coeff_inputs=int(inputs[1].get())

			if char_inputs and coeff_inputs:
				input_value.append((char_inputs,coeff_inputs))

		self.add_valNotes(input_value)

		self.outAdd_valid.grid_forget()
		self.note_lab.grid_forget()
		self.coeff_lab.grid_forget()
		for inputs in self.combo_widg_add:
			inputs[0].grid_forget()
			inputs[1].grid_forget()

		for val in self.order_notes:
			val.grid_forget()



	def set_view(self):
		self.outFrm_Vavg.pack_forget()
		rows=self.get_valNotes()
		self.outView_notes.config(state="normal")
		self.outView_notes.delete("1.0","end")
		if rows:
			for row in rows:
				text="Note :  {0}  |Coefficient :  {2}   |Valeur :  {1}\n".format(row[0],row[2],row[3])
				self.outView_notes.insert("end", text)
		else:
			self.outView_notes.insert("end","This block is empty")
		self.actneighb.actBtn_avg.grid(column=3, row=1,padx=15, pady=15)
		self.outView_notes.config(state="disabled")



	def set_avg(self):
		self.outView_avg.config(state="normal")
		avg_txt=self.get_valAvg(self.get_valNotes())

		self.outFrm_Vavg.pack(side=tk.RIGHT, anchor="n")
		self.outView_avg.delete("1.0","end")
		self.outView_avg.insert("end", avg_txt)
		self.outView_avg.config(state="disabled")
		


	def get_valNotes(self):
		rows=Db_handling.req_dbNote("", blockIn_name)
		return rows



	def get_valAvg(self, rows):
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


	def add_valNotes(self,list_notation):
		out=Db_handling.add_dbNotes('',blockIn_name,list_notation)
		if out:
			aMsg.set('All notes have been added')	
		else:
			aMsg.set("The notes can't be added")


	def del_block(self):
		global iid
		if tkmsg.askyesno("Delete","Do you really want to delete "+blockIn_name+" ?"):
			if Db_handling.del_dbBlock("",blockIn_name):
				select_area.tree_delete("")
				select_area.synch_treeview(selfSelect_area)
				aMsg.set(blockIn_name+" succesfully deleted !")
				Name.set("")
				iid=""
			else:
				aMsg.set("Something went wrong...")

	def rename_block(self):
		self.error_msg=tk.StringVar()
		self.tp_rename=tk.Toplevel()
		self.tp_rename.title("Rename")
		self.tp_rename.geometry("200x150")
		self.lab_tp=tk.Label(self.tp_rename, text="New name :")
		self.lab_tp.pack()
		self.ent_tp=tk.Entry(self.tp_rename)
		self.ent_tp.pack()
		self.ent_tp.focus_set()
		self.ent_tp.bind('<Return>',self.rename_valEty)
		self.but_tp=tk.Button(self.tp_rename,text="Rename", command=self.rename_valEty)
		self.but_tp.pack()
		self.lab_error=tk.Label(self.tp_rename, textvariable=self.error_msg)
		self.lab_error.pack()

	def rename_valEty(self,*event):
		global blockIn_name
		self.newname=str(self.ent_tp.get())
		if self.newname and self.newname!='':
			Db_handling.rename_dbBlock('',blockIn_name,self.newname)
			selfSelect_area.rename_this_block(self.newname)
			self.error_msg.set(blockIn_name+" is now "+self.newname+" !")
			selfSelect_area.update_subtree()
			self.quit_rename=tk.Button(self.tp_rename, text="Close", command=self.tp_rename.destroy)
			self.quit_rename.pack()
		else:
			self.error_msg.set("Please enter Something")


	def get_neighboor(self,neigh):
		self.actneighb=neigh



########## Action panel (=Action bar)

class Actbar(tk.Frame):
	def __init__(self, parent, *args, **kwargs):
		global blockIn_name, aMsg

		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.parent=parent

		self.outneighb=args[0]
		self.config( bg="white", height=125)

		self.bg='#404040'
		aMsg=tk.StringVar()
		
		# To prevent indexError in get_iidBlk
		blockIn_name = ''
		

		# Selection of actions area
			# Title
		self.act_ttl=tk.Label(self,text="Select an action :")
		self.act_ttl.grid(column=0, row=0, columnspan=2)

			# Button add notes
		self.actBtn_add=tk.Button(self,padx=5,pady=2, text="Add", command=lambda:self.get_action(act_frames[0],6))
		self.actBtn_add.grid(column=1, row=1,padx=15, pady=15)
			# Button view notes
		self.actBtn_view = tk.Button(self,padx=5,pady=2, text="View", command=lambda:self.get_action(act_frames[1],1))
		self.actBtn_view.grid(column=2, row=1,padx=15, pady=15)

			# Button view average
		self.actBtn_avg=tk.Button(self,padx=5,pady=2, text="Average", command=lambda:self.get_action('',3))
		
			# Button simulation notes
		self.actBtn_sim = tk.Button(self,padx=5,pady=2, text="Simulation", command=lambda:self.get_action(act_frames[2],4))
		self.actBtn_sim.grid(column=4, row=1,padx=15, pady=15)

			# Button rename block
		self.actBtn_rnm = tk.Button(self,padx=5,pady=2, text="Rename", command=lambda:self.get_action("",5))
		self.actBtn_rnm.grid(column=5, row=1,padx=15, pady=15)
		
			# Button delete block
		self.actBtn_del=tk.Button(self,padx=5,pady=2, text="Delete", command=lambda:self.get_action('',9))
		self.actBtn_del.grid(column=6, row=1,padx=15, pady=15)

			# Message status
		self.actMsg=tk.Label(self, textvariable=aMsg,bg="white", fg="blue")
		self.actMsg.grid(row=2,columnspan=15,column=0,padx=20, pady=5, sticky="e")



	def get_action(self,widget,act,*arg):

		# If any block is selected
		if not blockIn_name:
			tkmsg.showwarning("Select a block","No block selected, please choose one")

		# If block and button action is 3 (average button)
		elif blockIn_name and act==3:
			Outarea.set_avg(self.outneighb)

		# if action is rename
		elif blockIn_name and act==5:
			Outarea.rename_block(self.outneighb)

		# if action is delete
		elif blockIn_name and act==9:
			Outarea.del_block(self.outneighb)

		# if other action
		elif blockIn_name and act:
			# forget pack
			for frame in act_frames: frame.pack_forget()

			#forget grid button avg
			self.actBtn_avg.grid_forget()

			# packing widgets (frames)
			widget.pack(fill="both", expand=1)

			#if aciton is view
			if act==1:Outarea.set_view(self.outneighb)

			#if aciton is simulation
			elif act==4:self.outneighb.outSim_spn.focus_set()




########## Main Window (=Main != root)

class MainWindow:
	def __init__(self, master):
		self.master=master
		self.toolbar=Toolbar(self.master)
		self.navbar=Navbar(self.master)
		self.outarea=Outarea(self.master)
		self.actbar=Actbar(self.master, self.outarea)
		self.outarea.get_neighboor(self.actbar)

		self.btn_quit = tk.Button(self.master, text="Quit", command=lambda:quit_app(self.master), width=10, justify="center")

		self.Special_cmd()

		self.master.rowconfigure(2, weight=1)
		self.master.columnconfigure(1, weight=1)

		self.navbar.grid(column=0,row=0 ,rowspan=3,  sticky="swne")
		self.outarea.grid(column=1, rowspan=3,row=0,sticky="swne")
		self.actbar.grid(column=1, row=2, sticky="s", pady=15)
		self.btn_quit.grid(column=0, row=2, sticky="s", pady=15)

		# Binding 
			# Resize master
		self.master.bind("<Configure>", self.resize)
		self.fullScreenState = False
		self.master.bind("<F11>", self.toggleFullScreen)
		self.master.bind("<Escape>", self.quitFullScreen)



	def Special_cmd(self):
		self.toolbar.mainWin_cmd(self.toggleFullScreen)


	def toggleFullScreen(self, *event):
		self.fullScreenState = not self.fullScreenState
		self.master.attributes("-fullscreen", self.fullScreenState)

	def quitFullScreen(self, *event):
		self.fullScreenState = False
		self.master.attributes("-fullscreen", self.fullScreenState)

	def resize(self,event):
		print("New size is: {}x{}".format(event.width, event.height))



class Db_handling:
	def __init__(self):
		global cursor, conn

		# Looking for directory (data dir)
		os.makedirs("data") if not os.path.isdir('data') else ''

		# Looking for database file (data file)
		if os.path.isfile('data/note_base.db'):
			conn = sqlite3.connect('data/note_base.db')
			cursor = conn.cursor()

		else:
			Db_creation()



	def Db_creation(self):
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


	# get id of the block
	def get_dbIdBlk(self, name_block):
		cursor.execute("SELECT id FROM blocs WHERE name=?",(name_block,))
		id_of_bloc=cursor.fetchall()
		return id_of_bloc[0][0]


	# get list of blocks in db
	def get_dbBlk_list(self):
		cursor.execute("""SELECT name, semestre FROM blocs""")
		rows=cursor.fetchall()
		blks=[row for row in rows]

		return blks



	def add_dbBlk(self, *args):
		cursor.executemany("INSERT INTO blocs(name,semestre) VALUES (?,?)",*args)
		conn.commit()



	def del_dbBlock(self, name):
		id_blk=Db_handling.get_dbIdBlk("",name)
		try:
			cursor.execute("DELETE FROM notes WHERE id_bloc=?",(id_blk,))
			cursor.execute("DELETE FROM blocs WHERE id=?",(id_blk,))
			conn.commit()
		except:
			return False
		return True


	# request to get all notes with their values etc.. for the block
	def req_dbNote(self, name):
		id_blk=Db_handling.get_dbIdBlk("", name)
		cursor.execute("SELECT notes.note, notes.id, conversion.value, notes.coef,SUM(notes.coef) OVER() from notes INNER JOIN conversion WHERE notes.note=conversion.denomination and notes.id_bloc=? GROUP BY notes.id",(id_blk,))
		rows=cursor.fetchall()
		return rows


	def add_dbNotes(self,name,values):
		id_blk=Db_handling.get_dbIdBlk('',name)
		e_verif=True
		for value in values:
			try:
		 		cursor.executemany("""
	 				INSERT INTO notes(id_bloc,coef,note) VALUES(?, ?, ?)""",[(id_blk,value[1],value[0])])
			except:
				e_verif=False
				break
				
		if e_verif:
			conn.commit()
			return e_verif	
		else:
			conn.rollback()
			return e_verif


	def rename_dbBlock(self, oldname, newname):
		try:
			cursor.execute("UPDATE blocs SET name=? WHERE name=?",(newname,oldname,))
			conn.commit()
			return True
		except:
			return False




def get_iidBlk():
	global blockIn_name, cycleIn

	id_spl=id_foc.split("_")

	# get cycle in
	cycleIn="_"+id_spl[1]+"_"+id_spl[2]
	
	# get name of the block
	if id_spl[0]!='':
		blockIn_name=id_spl[0]
		out_ttlVal.set("Working on "+blockIn_name)



def quit_app(root):
	if tkmsg.askokcancel("Quit ?","You're gonna leave"):
		root.destroy()
		os.system("TASKKILL /IM python.exe /F") #stop the repl sublim text



def main():
	root=tk.Tk()
	root.title("Title here")
	root.geometry("1200x600")
	root.state('zoomed')
	Db_handling()
	MainWindow(root)
	root.mainloop()


if __name__=="__main__":
	main()


def add_block(name):
	cursor.execute("INSERT INTO blocs(name,semestre) VALUES (?,2)",(name,))
	conn.commit()
	print(name+ " has been added")
	print("\n\n---------- Working on",name,"----------\n")
	menu(name)

def del_block(intit):
	rep=input("\nDo you really want to delete the block "+intit+" ? (yes/no)\n")
	if rep == "yes":
		print("Deleting...")
		cursor.execute("DELETE FROM notes WHERE id_bloc=(SELECT id FROM blocs WHERE name =?)",(intit,))
		cursor.execute("DELETE FROM blocs WHERE name=?",(intit,))
		conn.commit()
		print("The block "+intit+" has been deleted")
	else:
		print("Going back to the selection menu\n")
	selectblock()


def add_noteinblock(name_block):
 	print("\nAdd notes in block")
 	valid_notes=("A","B","C","D")
 	nb_inblock=int(input(bfr + "Nbr of notes : "))

 	cursor.execute("SELECT id FROM blocs WHERE name=?",(name_block,))
 	id_of_bloc=cursor.fetchall()

 	for i in range(1,nb_inblock+1):
 		coeff = int(input(bfr+"Coef note " +str(i)+" : "))
 		notes = input(bfr+"Note " +str(i)+" : ")
 		notes=notes.upper()
 		if notes not in valid_notes:
 			print("You have entered the wrong value for : Note "+str(i)+"\nPlease retry...\n")
 			add_noteinblock(name_block)
 
 		cursor.executemany("""
 			INSERT INTO notes(id_bloc,coef,note) VALUES(?, ?, ?)""",[(id_of_bloc[0][0],coeff,notes)])

 	cursor.execute("SELECT coef, note FROM notes WHERE id_bloc=?",(id_of_bloc[0][0],))
 	conn.commit()
 	calc = cursor.fetchall()
 	print(calc)
 	noteinblock(name_block,req_note(name_block))

def del_noteinblock(name):
	print("Which one do you want to delete ?")


def req_note(name_block):
	cursor.execute("SELECT notes.note, notes.id, conversion.value, notes.coef,SUM(notes.coef) OVER() from notes INNER JOIN conversion WHERE notes.note=conversion.denomination and notes.id_bloc=(SELECT id FROM blocs WHERE name=?) GROUP BY notes.id",(name_block,))
	rows=cursor.fetchall()
	return rows

def moyinblock(name_block, req):
	if not req:
		print(bfr+"There is no notes in this block, please add them first")
		menu(name_block)

	tot_note=0
	tot_val=req[0][4]

	print("Calculating your average note...")
	for row in req:
		tot_note += (row[2]*row[3])
	avg = tot_note/tot_val
	if avg>=3.6 and avg<4.6:
		note_avg="B"
	elif avg>=4.6:
		note_avg="A"
	elif avg<3.6 :
		note_avg="not validated"
	print("Your current average is :",avg,"\nYour score in this block is",note_avg,"\n")
	return tot_note, tot_val

def noteinblock(name_block,rows):
	for row in rows:
		print("Note :  {0}  |Valeur :  {1}  |Coefficient :  {2}".format(row[0],row[2],row[3]))
	moyinblock(name_block, rows)


def sim_note(name):
	tot_note, tot_sadd=moyinblock(name,req_note(name))
	coeff_lft=0
	coeff_uni=[]
	quest=False
	while quest==False:
		nbr_lft=int(input("Number of notes to simulate (4 max) in "+name+"\n"))
		if nbr_lft<5 and nbr_lft>0:
			quest=True

	for i in range(1,nbr_lft+1):
		coeff = int(input("Coeff note "+str(i)+" : "))
		coeff_lft+=coeff
		coeff_uni.append(coeff)

	all_comb=list(itertools.product("5421", repeat=nbr_lft)) #All combinaisons
	print("Loading ...\n")

	list_fin_A=[]
	list_note_A=[]
	list_fin_B=[]
	list_note_B=[]
	
	for w in range(len(all_comb)):
		tot_inlist=0
		for j in range(nbr_lft):
			tot_inlist+=int(all_comb[w][j])*coeff_uni[j]

		moy_new=(tot_note+tot_inlist)/(tot_sadd+coeff_lft)
		if moy_new>=3.6 and moy_new<4.6:
			list_fin_B.append(all_comb[w])

		if moy_new>=4.6:
			list_fin_A.append(all_comb[w])


	print("\nTo B :")

	if not list_fin_B:
		print("Impossible to get B with this number of notes...")
	else:
		for ibis in range(len(list_fin_B)):
			buffe=[]
			for jibis in range(nbr_lft):
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
			print("Combinaison ",a," : {0} | (coeff {1})".format(list_note_B[a-1], coeff_uni))

	print("\nTo A :")
	if not list_fin_A:
		print("Impossible to get A with this number of notes...")
	else:
		for ibis in range(len(list_fin_A)):
			buffe=[]
			for jibis in range(nbr_lft):
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
			print("Combinaison ",a," : {0} | (coeff {1})".format(list_note_A[a-1], coeff_uni))




def rename_block(name):
	rep_rename=input("\nWrite a new name for the block "+name+" : ")
	cursor.execute("UPDATE blocs SET name=? WHERE name=?",(rep_rename,name,))
	rep_valid=input("Are you sure to rename "+name+" into "+rep_rename+" ? yes/no\n")
	if rep_valid=="yes":
		conn.commit()
		print("The name has been modified")
		menu(rep_rename)
	else:
		print('Going back to the menu...\n')
		conn.rollback()
		menu(name)


def menu(name):
	try:
		action=int(input("\nWhat do you want to do ?\n0 - Simulation\n1 - Add notes\n2 - Delete notes (not available)\n3 - See your notes\n4 - Only the average\n5 - Rename the block\n6 - Choose another block\n7 - Delete "+name+"\n8 - Quit\n"))

	except:
		print("Error, invalid entry\nPlease retry")
		menu(name)
	
	if action==0:
		sim_note(name)
	elif action==1:
		add_noteinblock(name)
	elif action==2:
		del_noteinblock(name)
	elif action==3:
		noteinblock(name,req_note(name))
	elif action==4:
		moyinblock(name,req_note(name))
	elif action==5:
		rename_block(name)
	elif action==6:
		selectblock()
	elif action==7:
		del_block(name)
	elif action==8:
		leaveall()
	else:
		print("Error, invalid entry : Value out of range\nPlease retry")
	menu(name)


def selectblock():
	inrow=[]

	cursor.execute("""SELECT name FROM blocs""")
	rows=cursor.fetchall()
	print("\n\nAll the blocks :")
	for row in rows:
		print("{0}".format(row[0]))

	theblock=str(input("\nChoose your block (if you want to leave write 'exit'): "))
	for row in rows:
		inrow.append(row[0])

	if theblock in inrow:
		print("Block",theblock,"found")
		print("\n---------- Working on",theblock,"----------")
		menu(theblock)
	elif theblock=="exit":
		leaveall()

	else:
		add_block(theblock)


def creation_db():
	global cursor,conn
	try:
		conn = sqlite3.connect('data/myown.db')
		cursor = conn.cursor()
		cursor.execute('CREATE TABLE blocs(id INTEGER PRIMARY KEY NOT NULL, name VARCHAR(30), semestre INT);')

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


def leaveall():
	conn.close()
	#If the repl doesn't close and create a locked database, be carrefull it stop every python processus running
	os.system("TASKKILL /IM python.exe /F")
	quit()


import os.path, sqlite3, itertools


bfr = "|  "

if not os.path.isdir('data'):
	os.makedirs("data")

# Vérifier si le fichier existe ou non
if os.path.isfile('data/myown.db'):
    print("Fichier trouvé")
    conn = sqlite3.connect('data/myown.db')
    cursor = conn.cursor()

else:
	print("Création de la base de donnée")
	creation_db()
selectblock()

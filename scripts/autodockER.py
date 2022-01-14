
"""
This script is setup to be run with a specific directory structure:

DISCO
|Gene
 |PDB
  |ligand file, receptor file, etc.
  
For each ligand-receptor pair, docking is performed and RMSD calculated from original crystal strucutre given in PDB folder
Smina calls (lines 49-57) have specific information on parameters and such
"""

import os
from pymol import cmd

# main function
def main():
	ligand_file = ""

	os.chdir("/media/noah/1E7A-DEB2/DISCO")

	files = os.listdir()
	
	# loop through all "outer" files according to the structure above
	for f in files:
		os.chdir("/media/noah/1E7A-DEB2/DISCO/" + f) 
		
		# inner files
		for fi in os.listdir():
			if "Cros" in fi:
				continue
			os.chdir("/media/noah/1E7A-DEB2/DISCO/" + f + "/" + fi)

			# Simple iterative search for ligand/target files
			for g in os.listdir(): 
				print(g)
				if "_LIG" in g or "_LIG0" in g:
					ligand_file = g
					print("ligand file = {}".format(ligand_file))
				elif "_PRO" in g:
					target_file = g
					print("target file = {}".format(target_file))
				else:
					continue
					
			# calculating center of mass may be wonky
			# due to error "mass is zero"
			try:

				cmd.load(ligand_file)
				cmd.load(target_file)
				center_coords = cmd.centerofmass(ligand_file[:-4])
			except:
				print("\nProblems determining center of mass\n")
				continue

			print("\nDocking {} to {}".format(ligand_file, target_file))

			# Initial smina call - docking of ligand to receptor 
			os.system("""/home/noah/Desktop/smina/smina.static -r {receptor} -l {ligand} --center_x {x_coord} --center_y {y_coord} --center_z {z_coord} --autobox_ligand {ligand} --exhaustiveness 8 --num_modes 9 --atom_terms {termfile_name} -o {outfile_name} --custom_scoring {scoring_file}
				""".format(receptor = target_file, ligand = ligand_file, 
					x_coord = center_coords[0], y_coord = center_coords[1],
					z_coord = center_coords[2], termfile_name = ligand_file[:4] + "_terms.at",
					outfile_name = ligand_file[:4] + "_out.pdb", scoring_file = "/home/noah/customscore.score"))

			# Secondary smina call - recereating initial cosrystal pose, due to isues with the RMSD calculation and format of smina output vs. preexisting smina output format
			os.system("""/home/noah/Desktop/smina/smina.static -r {receptor} -l {ligand} --center_x {x_coord} --center_y {y_coord} --center_z {z_coord} --autobox_ligand {ligand} --minimize_iters 1 --local_only -o {outfile_name} --custom_scoring {scoring_file}""".format(receptor = target_file, ligand = ligand_file, 
					x_coord = center_coords[0], y_coord = center_coords[1],
					z_coord = center_coords[2], outfile_name = ligand_file[:4] + "_rnamed.pdb", scoring_file  = "/home/noah/customscore.score"))

			dat = ""

			# Concatenation of unchanged crystal structure with docking resulting .pdb file, to make RMSD calculation easy
			try:
				with open(ligand_file[:4] + "_rnamed.pdb") as rnamed_file:
					dat = rnamed_file.read()

				dat += "\n"

				with open(ligand_file[:4] + "_out.pdb") as out:
					og_dat = out.read()

				dat += og_dat

				with open(ligand_file[:4] + "_FINAL.pdb", "w") as file:
					file.write(dat)

				# RMSD calculations using intra_fit()
				cmd.load(ligand_file[:4] + "_FINAL.pdb")
				rmsds = cmd.intra_fit(ligand_file[:4] + "_FINAL")

				i = 1
				with open("rmsd_calculations.txt", "w") as out:
					for r in rmsds:
						out.write("Pose " + str(i) + ": " + str(r) + "\n")
						i+=1
			except:
				continue		
			cmd.delete(ligand_file)
			cmd.delete(target_file)	

if __name__ == '__main__':
	main()	

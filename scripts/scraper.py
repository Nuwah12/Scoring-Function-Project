import os
import pandas as pd

"""
Once again, this script depends on the file structure outlined in autodockER.py

This scrapes the interaction terms, computes RMSDs, and scrapes affinities
"""

DEFAULT_DIR = "/home/noah/Desktop/refined-set"
def main():
	termfile = None
	rmsdfile = None
	master = []
	inner = []
	aff = None

	os.chdir(DEFAULT_DIR)
	for f in os.listdir():
		os.chdir(DEFAULT_DIR + "/" + f)
		files = findCriticalFiles()
		if files[3] == False:
			continue

		with open(files[1], "r") as rmsds:
			linecount = 1
			for line in rmsds:
				line = line.split()
				if float(line[2]) <= 1.5 and float(line[2]) != -1.0:
					aff = getAffinity(linecount, files[2])
					print("Affinity:", aff)
					inner.append(aff)
					inner.append(f)
					inner.append(float(line[2]))
					for g in getTerms(files[0], linecount):
						inner.append(g)
				linecount += 1
				master.append(inner)
				inner = []
				#print(master)
	toCSV(master)

def getTerms(termfile, pose):
	pose_count = 1
	gauss = []
	posgauss= []
	repulsion = []
	hydrophobic = []
	hbond = []
	comp = []

	with open(termfile, "r") as terms:
		for line in terms:
			if "END" in line:
				pose_count += 1
			elif pose_count == pose and "atomid" not in line:
				line = line.split()
				gauss.append(line[1])
				posgauss.append(line[2])
				repulsion.append(line[3])
				hydrophobic.append(line[4])
				hbond.append(line[5])
			elif pose_count > pose:
				break
	comp.append(gauss)
	comp.append(posgauss)
	comp.append(repulsion)
	comp.append(hydrophobic)
	comp.append(hbond)

	return comp

def findCriticalFiles():
	termfile = None
	rmsdfile = None
	outfile = None
	for l in os.listdir():
		if "_terms" in l:
			print("termfile: ", termfile)
			termfile = l
		elif "rmsd" in l:
			rmsdfile = l
			print("rmsdfile: ", rmsdfile)
		elif "_out" in l:
			outfile = l
	if termfile != None and rmsdfile != None:
		return [termfile, rmsdfile, outfile, True]
	else:
		return [termfile, rmsdfile, outfile, False]

def getAffinity(pose, inf):
	currpose = 1
	print("Outfile for affinity:", inf)
	with open(inf, "r") as infile:
		for line in infile:
			if "ENDMDL" in line:
				currpose+=1
			elif "minimizedAffinity" in line and currpose == pose:
				line = line.split()
				return line[2]
			

def toCSV(arr):
	os.chdir(DEFAULT_DIR)
	df = pd.DataFrame(arr)
	df.to_csv("refined-set-terms.csv")

if __name__ == '__main__':
	main()

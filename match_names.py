import re
import Levenshtein


def get_confidence(name1, name2):
	name1, name2 = name1.lower(), name2.lower()
	
	if name1 == name2:
		return 1
	elif re.sub(r'\W+|_', '', name1) == re.sub(r'\W+|_', '', name2):
		return 0.96
	name1, name2 = re.sub(r'\W+|_', ' ', name1), re.sub(r'\W+|_', ' ', name2)
	name1, name2 = re.sub(r'\s+', ' ', name1.strip()), re.sub(r'\s+', ' ', name2.strip())
	name1, name2 = re.sub(r'\bjr\b', ' junior ', name1).strip(), re.sub(r'\bjr\b', ' junior ', name2).strip()
	name1, name2 = re.sub(r'\bsr\b', ' senior ', name1).strip(), re.sub(r'\bsr\b', ' senior ', name2).strip()
	name1_l, name2_l = name1.split(), name2.split()
	
	# Difference of junior
	if ('junior' in name1 and 'junior' not in name2) or ('junior' in name2 and 'junior' not in name1):
		return 0.8*Levenshtein.ratio(name1, name2)
	# Difference of senior
	elif ('senior' in name1 and 'senior' not in name2) or ('senior' in name2 and 'senior' not in name1):
		return 0.8*Levenshtein.ratio(name1, name2)
	# Middle name missing
	elif abs(len(name1_l) - len(name2_l))<=1:
		if name1_l[0] == name2_l[0] and name1_l[-1] == name2_l[-1]:
			return 0.94
	return Levenshtein.ratio(name1, name2)
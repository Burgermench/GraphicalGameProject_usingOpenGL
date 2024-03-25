# credits: Margarida Moura, CGr 2022
#
"""Read vertices from OBJ file"""
from typing import List
def my_obj_reader(filename :str) -> List:
	"""Get the vertices from the file"""
	position_list = list()
	uv_list = list()

	vertices = list()
	uv = list()

	with open(filename, 'r') as in_file:
		has_vt = False
		for line in in_file:
			if line[0:2] == 'v ':
				point = [float(value) for value in line.strip().split()[1:]]
				vertices.append(point)
			elif line[0:2] == 'vt':
				has_vt = True
				point = [float(value) for value in line.strip().split()[1:]]
				uv.append(point)
			elif line[0] == 'f':

				if has_vt:
					face_description_pos = [int(value.split('/')[0])-1 for value in line.strip().split()[1:]]
					for elem in face_description_pos:
						position_list.append(vertices[elem])
					face_description_uv = [int(value.split('/')[1])-1 for value in line.strip().split()[1:]]
					for elem in face_description_uv:
						uv_list.append(uv[elem])
				else:
					face_description = [int(value) - 1 for value in line.strip().split()[1:]]
					for elem in face_description:
						position_list.append(vertices[elem])
	return position_list, uv_list

if __name__ == '__main__':
	f_in = input("File? ")
	result = my_obj_reader(f_in)
	print(result)
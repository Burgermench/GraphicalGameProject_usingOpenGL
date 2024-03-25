"""Read vertices from OBJ file"""
from typing import List

def my_obj_reader(filename: str) -> List:
    """Get the vertices from the file"""
    position_list = list()
    uv_list = list()

    vertices = list()
    uv = list()

    with open(filename, 'r') as in_file:
        for line in in_file:
            if line.startswith('v '):
                point = [float(value) for value in line.strip().split()[1:]]
                vertices.append(point)
            elif line.startswith('vt'):
                point = [float(value) for value in line.strip().split()[1:]]
                uv.append(point)
            elif line.startswith('f'):
                face_description = line.strip().split()[1:]
                for elem in face_description:
                    if '/' in elem:
                        indices = elem.split('/')
                        vertex_index = int(indices[0]) - 1
                        position_list.append(vertices[vertex_index])
                        if len(indices) > 1 and indices[1]:
                            uv_index = int(indices[1]) - 1
                            uv_list.append(uv[uv_index])
                    else:
                        position_list.append(vertices[int(elem) - 1])
    return position_list, uv_list

if __name__ == '__main__':
    f_in = input("File? ")
    result = my_obj_reader(f_in)
    print(result)

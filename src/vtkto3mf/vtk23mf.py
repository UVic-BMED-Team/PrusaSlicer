import sys
import meshio
import xml.etree.ElementTree as et
from xml.dom import minidom
import threading
import math

"""
TODO:
* clean up code and make common portions into functions
* add command line arguments (vtk_file, 3mf_file, number of threads)
"""

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = et.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def makeHeaders():
    model = et.Element('model')
    metadata = et.SubElement(model, 'metadata')
    metadata.text = 'metadata'
    rsc = et.SubElement(model, 'resources')
    return model, rsc

def writeVertices(points, vertices, start, end):
    for i in range(start, end):
        vertex = et.SubElement(vertices, 'vertex', {
            'x': str(points[i][0]),
            'y': str(points[i][1]),
            'z': str(points[i][2])
        })

def writeTriangle(cell, density, shapes, j, k, m):
    return et.SubElement(shapes, 'triangle', {
            'v1': str(cell[j]),
            'v2': str(cell[k]),
            'v3': str(cell[m]),
            'density': str(density[0])
        })

def writeShapes(cells, densities, parent):
    shapes = et.SubElement(parent, 'triangles')
    for i in range(len(cells)):
        tri0 = writeTriangle(cells[i], densities[i], shapes, 0, 1, 2)
        tri1 = writeTriangle(cells[i], densities[i], shapes, 0, 1, 3)
        tri2 = writeTriangle(cells[i], densities[i], shapes, 0, 2, 3)
        tri3 = writeTriangle(cells[i], densities[i], shapes, 1, 2, 3)

def getvtk(args):
    global num_threads

    vtkfilepath = args[1]
    threemffilepath = args[2]
    if len(args) != 4:
        num_threads = 4 #default set to 4

    try:
        vtk_data = meshio.read(vtkfilepath)
    except:
        raise Exception('Could not open input vtk file')
    try:
        outputfile = open(threemffilepath, "a+")
    except:
        raise Exception('Could not open output 3mf file')

    print('Writing headers')
    model, resources = makeHeaders()
    vertobj = et.SubElement(resources, 'object')
    mesh = et.SubElement(vertobj, 'mesh')
    vertices = et.SubElement(mesh, 'vertices')
    print('Finished writing headers')

    print('Writing points')
    t = []
    numThreads = 4
    slices = []
    for i in range(numThreads):
        slices.append(math.floor(len(vtk_data.points)/numThreads*i))
    slices.append(numThreads-1)

    for i in range(numThreads):
        start = slices[i]
        end = slices[i+1] - 1
        thread = threading.Thread(target=writeVertices, args=(vtk_data.points, vertices, start, end))
        t.append(thread)

    for thread in t:
        print('Starting thread')
        thread.start()

    for thread in t:
        thread.join()
    print('Finished writing points')

    #vertices = writeVertices(output.points, resources)
    shapes = vtk_data.cells[0][1]
    densities = vtk_data.cell_data['HU-Intensity'][0]
    print('Writing shapes')
    writeShapes(shapes, densities, mesh)
    print('Finished writing shapes')
    outputfile.write(prettify(model))
    print('Finished writing to file '+threemffilepath)
    outputfile.close()

def check_arg_types(args):
    if args[1].split('.')[-1] != 'vtk' or args[2].split('.')[-1] != 'model':
        raise Exception('Must provide valid input vtk and output 3mf file paths')
    if len(args) == 4:
        try:
            global num_threads 
            num_threads = int(args[3])
        except:
            raise Exception('Number of threads is not of type integer')

if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        raise Exception('Must provide exactly 2 or 3 arguments: input vtk file, output 3mf file, (optional) number of threads')
    check_arg_types(sys.argv)
    getvtk(sys.argv)

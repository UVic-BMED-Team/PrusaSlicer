import meshio
import xml.etree.ElementTree as et
from xml.dom import minidom
import threading
import math


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = et.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def makeHeaders(output):
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

def writeShapes(cells, densities, parent):
    shapes = et.SubElement(parent, 'triangles')
    for i in range(len(cells)):
        tri0 = et.SubElement(shapes, 'triangle', {
            'v1': str(cells[i][0]),
            'v2': str(cells[i][1]),
            'v3': str(cells[i][2]),
            'density': str(densities[i][0])
        })
        tri1 = et.SubElement(shapes, 'triangle', {
            'v1': str(cells[i][0]),
            'v2': str(cells[i][1]),
            'v3': str(cells[i][3]),
            'density': str(densities[i][0])
        })
        tri2 = et.SubElement(shapes, 'triangle', {
            'v1': str(cells[i][0]),
            'v2': str(cells[i][2]),
            'v3': str(cells[i][3]),
            'density': str(densities[i][0])
        })
        tri3 = et.SubElement(shapes, 'triangle', {
            'v1': str(cells[i][1]),
            'v2': str(cells[i][2]),
            'v3': str(cells[i][3]),
            'density': str(densities[i][0])
        })

def getvtk(file):
    output = meshio.read(file)
    """
    print(type(output.points))
    for i in range(10):
        print(output.cells[0][1][i]) #cells
    
    for i in range(10):
        print(output.cell_data['HU-Intensity'][0][i][0]) #density data
    """
    outputfile = open("./output.model", "a+")
    model, resources = makeHeaders(outputfile)
    
    vertobj = et.SubElement(resources, 'object')
    mesh = et.SubElement(vertobj, 'mesh')
    vertices = et.SubElement(mesh, 'vertices')

    t = []
    numThreads = 4
    slices = []
    for i in range(numThreads):
        slices.append(math.floor(len(output.points)/numThreads*i))
    slices.append(numThreads-1)

    for i in range(numThreads):
        start = slices[i]
        end = slices[i+1] - 1
        thread = threading.Thread(target=writeVertices, args=(output.points, vertices, start, end))
        t.append(thread)

    for thread in t:
        thread.start()

    for thread in t:
        thread.join()

    #vertices = writeVertices(output.points, resources)
    shapes = output.cells[0][1]
    densities = output.cell_data['HU-Intensity'][0]
    writeShapes(shapes, densities, mesh)
    
    outputfile.write(prettify(model))

    outputfile.close()


if __name__ == "__main__":
    getvtk("./volume_celldata.vtk")
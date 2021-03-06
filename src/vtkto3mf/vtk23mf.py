import meshio
import xml.etree.ElementTree as et
from xml.dom import minidom


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

def writeVertices(output, points, rsc):
    vertobj = et.SubElement(rsc, 'object', {})
    mesh = et.SubElement(vertobj, 'mesh')
    vertices = et.SubElement(mesh, 'vertices')
    for xyz in points:
        vertex = et.SubElement(vertices, 'vertex', {
            'x': str(xyz[0]),
            'y': str(xyz[1]),
            'z': str(xyz[2])
        })
    return vertices

def writeShapes(output, cells, densities, parent):
    shapes = et.SubElement(parent, 'tetras')
    for i in range(len(cells)):
        shape = et.SubElement(shapes, 'tetra', {
            'v1': str(cells[i][0]),
            'v2': str(cells[i][1]),
            'v3': str(cells[i][2]),
            'v4': str(cells[i][3]),
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
    vertices = writeVertices(outputfile, output.points, resources)
    shapes = output.cells[0][1]
    densities = output.cell_data['HU-Intensity'][0]
    writeShapes(outputfile, shapes, densities, vertices)
    
    outputfile.write(prettify(model))

    outputfile.close()


if __name__ == "__main__":
    getvtk("./volume_celldata.vtk")
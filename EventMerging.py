import os, sys, glob
from xml.etree.ElementTree import Element, SubElement, ElementTree, parse

DIR_TO_ParentSave = '/media/ExtHDD001/viratXML'
WIDTH = 1960
HEIGHT = 1080

def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def xml_writer(info, PATH_TO_XML):

    # caculate height and width of image
    # KYH : I am not sure that every video has same resolutionfghos
    # So I should check every image
    # im = cv2.imread(PATH_TO_FILE.format('.xml'))  # load image
    # height = im.shape[0]  # calc image height
    # width = im.shape[1]  # calc image width

    PATH_TO_FRAME = PATH_TO_XML.split('.')[0] + ".jpg"

    # Generate xml format annotation file
    annotation = Element("annotation")
    SubElement(annotation, "folder").text = DIR_TO_ParentSave.split('/')[-1]
    SubElement(annotation, "filename").text = PATH_TO_FRAME.split('/')[-1]

    source = Element("source")
    SubElement(source, "database").text = "Unknown"
    annotation.append(source)

    size = Element("size")
    SubElement(size, "width").text = str(WIDTH)
    SubElement(size, "height").text = str(HEIGHT)
    SubElement(size, "depth").text = str(3)
    annotation.append(size)

    SubElement(annotation, "segmented").text = '0'


    for elem in zip(info[0], info[1]):
        object = Element("object")
        SubElement(object, "name").text = elem[1]
        SubElement(object, "pose").text = 'Unspecified'
        SubElement(object, "truncated").text = '0'
        SubElement(object, "difficult").text = '0'

        bndbox = Element("bndbox")
        SubElement(bndbox, "xmin").text = str(elem[0][0])
        SubElement(bndbox, "ymin").text = str(elem[0][1])
        SubElement(bndbox, "xmax").text = str(elem[0][2])
        SubElement(bndbox, "ymax").text = str(elem[0][3])
        object.append(bndbox)

        annotation.append(object)

    # orderingd XML data
    indent(annotation)

    # save XML annotation file
    xml_filename = PATH_TO_XML
    ElementTree(annotation).write(xml_filename)
    print("Save {}".format(PATH_TO_FRAME))


def getduplicatedXMLPath(Allxml, matchers):
    '''

    :param Allxml: have all xml name in DIR_TO_ParentSave
    :param matchers: have xml name without duplication
    :return:
    '''
    matching = []

    for matcher in matchers:
        matching.append([xml for xml in Allxml if matcher in xml.split('/')[-1]])

    # Remove lists that have one element (no duplication)
    duplicatedXML = [xml for xml in matching if len(xml) > 1]

    return duplicatedXML



if __name__ == "__main__":
    Allxml = [y for x in os.walk(DIR_TO_ParentSave) for y in glob.glob(os.path.join(x[0], '*.xml'))]

    matchers = set()
    for xml in Allxml:
        matchers.add(xml.split('/')[-1]) # get xml file names
    duplicatedXML = getduplicatedXMLPath(Allxml, matchers)

    for PATH_TO_XMLS in duplicatedXML:
        xmlTrees = []
        for PATH_TO_XML in PATH_TO_XMLS:
            xml = open(PATH_TO_XML,"r")
            xmlTrees.append(parse(xml))
        info = [[], []]
        for xmlTree in xmlTrees:
            root = xmlTree.getroot()
            for object in root.iter('object'):
                info[1].append(object.findtext("name"))
                for bndbox in object.iter('bndbox'):
                    info[0].append([bndbox.findtext("xmin"),
                                    bndbox.findtext("ymin"),
                                    bndbox.findtext("xmax"),
                                    bndbox.findtext("ymax")])
        # remove duplicated bbox
        for bbox in info[0]:
            index = [i for i, v in enumerate(info[0]) if v == bbox]
            for i in range(len(index)-1):
                info[0].pop(index[i])
                info[1].pop(index[i])
        PATH_TO_SAVEXML = os.path.join(DIR_TO_ParentSave, PATH_TO_XMLS[0].split('/')[-1])
        xml_writer(info, PATH_TO_SAVEXML)

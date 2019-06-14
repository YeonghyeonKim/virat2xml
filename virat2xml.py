'''
Author : KYH
Date : 2019-06-07
Description :
Convert Virat dataset json format to PASCAL VOC format

step1. Read and parse json file / Make XML basic format
step2. Fill XML file
step3. Save XML file

'''

import os, sys, glob
import json
import cv2
from xml.etree.ElementTree import Element, SubElement, ElementTree

activities = ('Opening', 'Closing', 'Open_Trunk', 'Closing_Trunk') # activities to be detected

DIR_TO_JSON = '/media/ExtHDD001/activity_net_dataset/Virat_dataset/actev-data-repo/partitions'
DIR_TO_VIDEO = ''

DIR_TO_ParentSave = 'Dataset'

WIDTH = 1960
HEIGHT = 1080


def GenActivitiesDir():
    '''
    Generate Activity directory
    In ITLAB Case (19/06/07),
    4 directories, 'Opening', 'Closing', 'Open_Trunk', and 'Closing_trunk', will be generated
    under DIR_TO_ParentSave
    '''
    for act in activities:
        DIR_TO_ActSave = os.path.join(DIR_TO_ParentSave, act)
        if not os.path.exists(DIR_TO_ActSave):
            print("Generate %s folder".format(DIR_TO_ActSave))
            os.makedirs(DIR_TO_ActSave)

def SaveFrame(cap, info, DIR_TO_ActSave):
    for numFrame in info.keys():
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(numFrame))
        ret, frame = cap.read()
        PATH_TO_FRAME = DIR_TO_ActSave+"_"+numFrame + ".jpg"
        print("Save {}".format(PATH_TO_FRAME))
        cv2.imwrite(PATH_TO_FRAME, frame)

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


def xml_writer(info, videoName, DIR_TO_ActSave):

    # caculate height and width of image
    # KYH : I am not sure that every video has same resolutionfghos
    # So I should check every image
    # im = cv2.imread(PATH_TO_FILE.format('.xml'))  # load image
    # height = im.shape[0]  # calc image height
    # width = im.shape[1]  # calc image width

    for numFrame in info:
        PATH_TO_FRAME = DIR_TO_ActSave+"_"+numFrame + ".jpg"

        # Generate xml format annotation file
        annotation = Element("annotation")
        # SubElement(annotation, "folder").text = img_path.split('/')[-2]
        SubElement(annotation, "filename").text = PATH_TO_FRAME

        source = Element("source")
        SubElement(source, "database").text = "Unknown"
        annotation.append(source)

        size = Element("size")
        SubElement(size, "width").text = str(WIDTH)
        SubElement(size, "height").text = str(HEIGHT)
        SubElement(size, "depth").text = str(3)
        annotation.append(size)

        SubElement(annotation, "segmented").text = '0'


        for elem in zip(info[numFrame][0], info[numFrame][1]):
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

        # ordering XML data
        indent(annotation)

        # save XML annotation file
        xml_filename = PATH_TO_FRAME.split(".")[0] + '.xml'
        ElementTree(annotation).write(xml_filename)
        print("Save {}".format(PATH_TO_FRAME))


if __name__ == "__main__":
    GenActivitiesDir()

    # Search activities.json files that have annotation info in all nested directories
    result = [y for x in os.walk(DIR_TO_JSON) for y in glob.glob(os.path.join(x[0], 'activities.json'))]
    for jsonfile in result:
        with open(jsonfile, 'r') as jfile:
            jdata = json.load(jfile)
            p_jdata = jdata['activities'] # parent node of json file
            for s_jdata in p_jdata:
                activity = s_jdata['activity']

                if not activity in activities: # if 'activity' is not target activity, skip
                    continue
                '''sub-sub-jdata
                ss_jdata format
                {'localization':
                    {VideoName :
                        sss_jdata
                    }
                'objectID':
                'objectType':
                }
                '''
                videoName = list(s_jdata['localization'])[0]
                PATH_TO_VIDEO = os.path.join(DIR_TO_VIDEO, videoName)
                cap = cv2.VideoCapture(videoName)
                if not cap.isOpened():
                    print("Can't find {}. To continue, press any keys".format(videoName))
                    input("")
                DIR_TO_ActSave = os.path.join(DIR_TO_ParentSave, activity, videoName.split(".")[0])
                info = dict()


                for ss_jdata in s_jdata['objects']:
                    '''sub-sub-sub jdata
                    sss_jdata format
                    {
                    'Frame' : {'boundingBox':{'h':~,'w':~,'x':~,'y':~}}, 
                    'Frame' : ~~
                    }
                    '''
                    sss_jdata = ss_jdata['localization'][videoName]
                    cls = ss_jdata['objectType']

                    ###################
                    for frame in sss_jdata:
                        try:
                            bbox = sss_jdata[frame]['boundingBox']
                        except:
                            continue

                        xmin = bbox['x']
                        ymin = bbox['y']
                        xmax = bbox['w'] + xmin
                        ymax = bbox['h'] + ymin
                        try:
                            info[frame][0].append([xmin, ymin, xmax, ymax])
                            info[frame][1].append(cls)
                        except:
                            info[frame]=[[],[]]
                            info[frame][0].append([xmin, ymin, xmax, ymax])
                            info[frame][1].append(cls)


                ## Save Frame
                SaveFrame(cap, info, DIR_TO_ActSave)

                ## Save XML
                xml_writer(info, videoName, DIR_TO_ActSave)
                info.clear()

import os
import json
from xml.etree.ElementTree import Element, SubElement, ElementTree
import cv2
"""
    bdd100k dataset json structure convert to xml file
    bbox structure x_min, y_min. x_max, y_max
"""

def check_double_slash(name):
    if not name.find('//') == -1:
        name = name.replace('//','/')
    return name

def createFolder(directory):
    try:
        if not os.path.isdir(directory):
            os.makedirs(directory)
    except OSError:
        print("Error: creating directory," + directory)

def indent(elem, level=1):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "   "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def write_to_xml(result, IMAGE_PATH, XML_SAVE_PATH, IMAGE_SAVE_PATH):
    #get image_name
    image_name = result['name']
    #get bboxes
    """
    category, x_min, y_min, x_max, y_max
    """
    bboxes_list = result['bbox']
    #get category
    category_list = result['category']
    
    root = Element('Annotations')
    SubElement(root,'filename').text = image_name

    img = cv2.imread(os.path.join(IMAGE_PATH,image_name))
    h,w,d = img.shape

    size = SubElement(root,'size')
    SubElement(size,'width').text = str(w)
    SubElement(size,'height').text = str(h)
    SubElement(size,'depth').text = str(d)

    for i in range(len(bboxes_list)):
        category = category_list[i]
        x_min = int(bboxes_list[i]['x1'])
        y_min = int(bboxes_list[i]['y1'])
        x_max = int(bboxes_list[i]['x2'])
        y_max = int(bboxes_list[i]['y2'])
        
        obj = SubElement(root,'object')

        SubElement(obj,'name').text = str(category)
        SubElement(obj,'difficult').text = str(0)

        bndbox = SubElement(obj,'bndbox')

        SubElement(bndbox,'xmin').text = str(x_min)
        SubElement(bndbox,'ymin').text = str(y_min)
        SubElement(bndbox,'xmax').text = str(x_max)
        SubElement(bndbox,'ymax').text = str(y_max)

    tree = ElementTree(root)
    indent(root)
    anno_path = XML_SAVE_PATH+"/"+image_name.split('.')[0] +'.xml'
    anno_path = check_double_slash(anno_path)
    img_path = IMAGE_SAVE_PATH+"/"+image_name
    img_path = check_double_slash(img_path)
    print(img_path)
    cv2.imwrite(img_path,img)
    tree.write(anno_path)


if __name__ == "__main__":
    """
        User can modify PATH information
    """
    XML_SAVE_PATH = "xml/"
    IMAGE_SAVE_PATH = "image/"
    TARGET_PATH = "det_20/det_train.json"
    IMAGE_PATH = "../images/100k/train/"
    CATEGORY = "car"  #if want various category, change str to list 

    #check TARGET_PATH
    if not os.path.isfile(TARGET_PATH):
        raise Exception("There is no that dir:",TARGET_PATH)
    
    #make save_path dir
    createFolder(XML_SAVE_PATH)
    createFolder(IMAGE_SAVE_PATH)

    #read json file
    result_list = []
    name_category_bbox = {}
    with open(TARGET_PATH,"r",encoding="utf8") as file:
        doc = json.load(file)
    
    for i in range(len(doc)):
        keyList = doc[i].keys
        name = doc[i]['name']
        count = 0
        category_list = []
        bbox_list = []
        #print(name)
        #print(keyList())
        if not doc[i].get('labels'):
            continue
        for k in range(len(doc[i]['labels'])):
            category = doc[i]['labels'][k]['category']
            if isinstance(CATEGORY,str) and category != CATEGORY:
                continue
            elif isinstance(CATEGORY,list) and category not in CATEGORY:
                continue
            count = 1
            bbox = doc[i]['labels'][k]['box2d']
            category_list.append(category)
            bbox_list.append(bbox)
        if not count == 0:
            #append
            name_category_bbox = {}
            name_category_bbox["name"] = name
            name_category_bbox["category"] = category_list
            name_category_bbox["bbox"] = bbox_list
            result_list.append(name_category_bbox)

    #generate xml file
    for result in result_list:
        write_to_xml(result,IMAGE_PATH,XML_SAVE_PATH,IMAGE_SAVE_PATH)
    print("Done covert to xml!")
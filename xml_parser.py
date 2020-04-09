import requests
import xml.etree.cElementTree as ET
import os
import datetime
import re
import openpyxl


class XML(object):

    def __init__(self, path: str):
        self.path_to = path
        self.array = []

    def _read_local(self, path_to):
        with open(path_to, "r") as f:
            text = f.read()
        f.close()
        return text

    def _read_http(self, path_to):
        r = requests.get(path_to)
        text = r.text
        return text

    def read(self):
        try:
            if "http" in self.path_to:
                text = self._read_http(self.path_to)
            else:
                text = self._read_local(self.path_to)
        except Exception as e:
            text = e
        return text

    def save_to_dir(self):
        parent_dir = "."
        # Check dir and create it, if dir is not there
        dirs = os.listdir(path=parent_dir)
        if "xml-files" not in dirs:
            os.mkdir(parent_dir+"/xml-files")
        # Write the xml file
        text = self.read()
        filename = "xml" + str(datetime.datetime.now()).replace(".", "-") + ".xml"
        with open(parent_dir+"/xml-files/" + filename, "w") as f:
            f.write(text)
            f.close()
        # Return path to file
        return parent_dir+"/xml-files/" + filename


class XMLParser(object):

    def __init__(self, path_to):
        self.path_to = path_to

    def get_offers_list_text(self):
        with open(self.path_to, 'r') as f:
            text = f.read()
        result = re.findall(r'<offer.*?</offer>', text)
        return result

    def ozon_offers_list(self):
        xml_tree = ET.parse(self.path_to)
        root = xml_tree.getroot()
        array = []
        for offer in root.iter("offer"):
            dict = {}
            dict["id"] = offer.attrib["id"]
            params = offer.getchildren()
            for param in params:
                children = param.getchildren()
                if len(children) > 0:
                    for attrib in children:
                        if attrib.tag == "attribute":
                            try:
                                dict[attrib.attrib["attrName"]] = attrib.attrib["attrValue"]
                            except:
                                dict[attrib.attrib["attrName"]] = ""
                else:
                    dict[param.tag] = param.text
            array.append(dict)
            self.array = array
        return array

    def get_all_keys(self):
        titles = []
        for dictionary in self.array:
            for key in dictionary:
                titles.append(key)
        return list(set(titles))

    def get_all_categories(self):
        cat_dict = {}
        with open(self.path_to, 'r') as f:
            text = f.read()
        cats = re.findall(r'<category id=.(\d+?). parentId=.*?>(.*?)</category>', text, flags = re.DOTALL)
        for cat in cats:
            cat_dict[int(cat[0])] = cat[1]
        return cat_dict

    def beru_offers_list(self):
        offers_list = []

        xml_tree = ET.parse(self.path_to)
        root = xml_tree.getroot()

        for offer in root.iter("offer"):
            offer_dict = offer.attrib
            params = offer.getchildren()
            for elem in params:
                if str(elem.tag) == "param":
                    offer_dict[str(elem.attrib["name"])] = str(elem.text).replace("&nbsp;", "")
                else:
                    offer_dict[str(elem.tag)] = str(elem.text).replace("&nbsp;", "")
                offers_list.append(offer_dict)
        return offers_list


# x = XML("input_xml/ozon_mvideo_mbt.xml")
# xml_file_dir = x.save_to_dir()

import yaml
import fnmatch
import os
import time
import pprint
from pathlib import Path

default_config_file = './default.yaml'

class Program:
    def __init__(self):
        self._printtypes = [str, int, float]

    def load_config(self, configFile):
        with open(configFile, 'r') as f:
            return yaml.load(f.read(), Loader=yaml.Loader)

    @staticmethod
    def printableType(value):
        if type(value) is str: return True
        if type(value) is int: return True
        if type(value) is float: return True
        if type(value) is bool: return True
        return False

    @staticmethod
    def presentKeyValues(title, config):
        print("%s:" % title.title())
        [print("- %s: %s" % (key.title(), config[key])) for key in config.keys() if Program.printableType(config[key])]

    @staticmethod
    def presentArray(title, array):
        print("%s:" % title.title())
        [print("- %s" % value) for value in array if Program.printableType(value)]

    @staticmethod
    def presentProperties(title, config, property, showKey=False):
        print("%s:" % title.title())
        if showKey:
            [print("- %s <- %s" % (config[key][property], key.title())) for key in config.keys() if Program.printableType(config[key][property])]
        else:
            [print("- %s" % (config[key][property])) for key in config.keys() if Program.printableType(config[key][property])]

    @staticmethod
    def extentionCategory(categoriesConfig):
        exts = {}
        for categoryKey in categoriesConfig.keys():
            category = categoriesConfig[categoryKey]
            for ext in category["extentions"]:
                exts[ext] = categoryKey
        return exts

    @staticmethod
    def resolveFilesInCategory(extentionCategory, scanFolder, excludes):
        catagoryFiles = {}
        for root, subdirs, files in os.walk(scanFolder):
            for fileName in files:
                if sum([1 for exclude in excludes if fnmatch.fnmatch("%s\\%s" % (root, fileName), exclude)]) == 0:
                    fileType = fileName.split(".")[-1]
                    if fileType in extentionCategory:
                        categoryName = extentionCategory[fileType]
                        if not categoryName in catagoryFiles: catagoryFiles[categoryName] = {
                            "files": [],
                            "count": 0
                        }

                        catagoryFiles[categoryName]["files"].append({
                            "root": root,
                            "filename": fileName,
                            "fullpath": "%s\\%s" % (root, fileName),
                            "stat": os.stat("%s\\%s" % (root, fileName))
                        })

                        catagoryFiles[categoryName]["count"] += 1;
        return catagoryFiles

    @staticmethod
    def generateFolderStructure(categoriesConfig, catagoryFiles):
        catAndConfs = [(cfk, categoriesConfig[cfk], catagoryFiles[cfk]) for cfk in categoriesConfig.keys() if cfk in catagoryFiles]
        structure = {}
        for catAndConf in catAndConfs:
            category, config, fGroup = catAndConf
            subcatFilter = config["subcategory"]
            subcats = []
            structure[config["name"]] = []
            for file in fGroup["files"]: 
                    value = "files"
                    if subcatFilter == "year":
                        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = file["stat"]
                        value = time.ctime(ctime).split(" ")[-1]
                    if not value in subcats: 
                        subcats.append(value)
                        structure[config["name"]].append(value)
        return structure
            
    def main(self, configFile):
        configRoot = self.load_config(configFile)
        configMas = configRoot["mas"]
        categoriesConfig = configMas["categories"]
        extToType = Program.extentionCategory(categoriesConfig)
        catagoryFiles = {}

        print("Setup Configuration")
        Program.presentKeyValues('configuration', configMas)
        Program.presentProperties('categories', categoriesConfig, 'name')
        Program.presentKeyValues('extentions', extToType)    
        Program.presentArray('exclusions', configMas["excludes"])

        catagoryFiles = Program.resolveFilesInCategory(extToType, configMas['scanfolder'], configMas["excludes"])

        print("Hydrating files")
        Program.presentProperties('category count', catagoryFiles, 'count', showKey=True)

        print("Building Folder Structure")
        structure = Program.generateFolderStructure(categoriesConfig, catagoryFiles)
        prt = pprint.PrettyPrinter(indent=4)
        prt.pprint(structure)

program = Program()
program.main(default_config_file)

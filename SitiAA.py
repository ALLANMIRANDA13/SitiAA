
from FunctionsPython import GetWorkDirectories,CreateWorkDir,ExtractZipFiles,ExtractXMLPath,CreateDataFrame, CreateAuditDataFrame, CreateTXT, CreateAuditFiles

directory = "/Users/allan/Desktop/SitiAA Python automatization/ZipFiles"

import os

def main():

    for i in GetWorkDirectories(directory):
        CreateWorkDir(i)
        ExtractZipFiles(i)

    for x in GetWorkDirectories(directory):
        xml_paths = ExtractXMLPath(x)
        oficiodf = CreateDataFrame(xml_paths)
        AuditDataframe = CreateAuditDataFrame(oficiodf)
        audit_folder = os.path.join(x,'Audit Files')
        CreateAuditFiles(AuditDataframe,audit_folder)
        CreateTXT(AuditDataframe, audit_folder)

if __name__ == '__main__':
    main()
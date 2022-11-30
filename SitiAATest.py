from operator import itemgetter
import os
import os.path
from bs4 import BeautifulSoup as bs
import pandas as pd
import dataframe_image as dfi
from datetime import date
import numpy as np
import unidecode
from difflib import SequenceMatcher
import shutil

directory = '/Users/allan/Desktop/SitiAA Python automatization/Zipfiles/B'

def CreateWorkDir(directory):
    directories_names = ['Download Oficios','Audit Files']
            
    for i in directories_names:
        new_directory_path = os.path.join(directory,i)
        if (os.path.exists(new_directory_path)):
            pass
        else:
            os.mkdir(new_directory_path)

print(CreateWorkDir(directory))

def ExtractXMLPath(directory):
    file_xml_paths = []
    for root, directories, files in os.walk(directory):
        for item in files:
            if item.endswith('.xml'):
                file_path = os.path.join(root, item)
                file_xml_paths.append(file_path)
    return file_xml_paths

xml_paths = ExtractXMLPath(directory)

def CreateDataFrame(xml_paths):

    NombreSolicitud = []
    RFC = []
    DomicilioSolicitud = []
    NumerOficio = []
    NumeroFolio = []
    OficioAño = []
    AreaOficio = []
    AutoridadOficio = []

    for i in xml_paths:
        with open(i, 'r') as f:
            data = f.read()
            content = "".join(data)
            bs_content = bs(content,"lxml")
            personassolicitud = bs_content.find_all("personassolicitud")
            cnbv_numerooficio = bs_content.find_all("cnbv_numerooficio")
            cnbv_folio = bs_content.find_all("cnbv_folio")
            cnbv_oficioyear = bs_content.find_all("cnbv_oficioyear")
            cnbv_areadescripcion = bs_content.find_all("cnbv_areadescripcion")
            autoridadnombre = bs_content.find_all("autoridadnombre")

            for i in personassolicitud:
                if i.persona.string == 'Moral':
                    name = i.nombre.string
                elif i.persona.string == 'Fisica':
                    name = str(i.nombre.string) +' '+ str(i.paterno.string) + ' ' + str(i.materno.string)
                NombreSolicitud.append(name)
                RFC.append(i.rfc.string)
                DomicilioSolicitud.append(i.domicilio.string)
                for z in cnbv_numerooficio:
                    oficio = z.string
                    NumerOficio.append(oficio)
                for y in cnbv_folio:
                    folio_number = int(y.string)
                    NumeroFolio.append(folio_number)
                for m in cnbv_oficioyear:
                    oficio_year = m.string
                    OficioAño.append(oficio_year)
                for r in cnbv_areadescripcion:
                    area_descripcion = r.string
                    AreaOficio.append(area_descripcion)
                for w in autoridadnombre:
                    autoridad_nombre = w.string
                    AutoridadOficio.append(autoridad_nombre)

    dataframe = pd.DataFrame({
        'Nombre':NombreSolicitud,
        'RFC': RFC,
        'Dirección': DomicilioSolicitud,
        'Numero Oficio': NumerOficio,
        'Folio': NumeroFolio,
        'Area': AreaOficio,
        'Autoridad': AutoridadOficio
         })

    return dataframe

dataframe = CreateDataFrame(xml_paths)

def CreateAuditDataFrame(dataframe):

    customerDB = pd.read_csv('/Users/allan/Desktop/SitiAA Python automatization/CUSTOMER DATABASE.csv')
    oficiodf = CreateDataFrame(xml_paths)
    ClientesICBC = customerDB['Nombre del Cliente'].unique().tolist()
    NombresOficios = oficiodf['Nombre'].tolist()
    
    ResultadosClientesICBC = []

    for i in NombresOficios:
        for j in ClientesICBC:
            
            string_01 = str(i).lower().casefold().strip().replace(',','').replace('.','')
            string_02 = str(j).lower().casefold().strip().replace(',','').replace('.','')
            string_01 = unidecode.unidecode(string_01)
            string_02 = unidecode.unidecode(string_02)
            ratio = SequenceMatcher(a=string_01, b=string_02).ratio()

            if ratio > 0.9:
                ResultadosClientesICBC.append(i) 
            else:
                pass

    ResultadosNOClientes = []

    for i in NombresOficios:
        if i not in ResultadosClientesICBC:
            ResultadosNOClientes.append(i)

    products_list = []

    for i in ResultadosClientesICBC:

        e = f"SE ENCONTRO RESULTADO"    
        df = oficiodf.loc[oficiodf['Nombre']==i] 
        df.insert(7, "CLIENTE ICBC", e )
        df_list = df.values.tolist()
        products_list.insert(0,df_list)
    
    for i in ResultadosNOClientes:
        e = f"NO SE ENCONTRO RESULTADO"
        df = oficiodf.loc[oficiodf['Nombre']==i] 
        df.insert(7, "CLIENTE ICBC", e )
        df_list = df.values.tolist()
        products_list.insert(0,df_list)

    NombreSolicitud = []
    RFC = []
    DomicilioSolicitud = []
    NumerOficio = []
    NumeroFolio = []
    OficioAño = []
    AreaOficio = []
    AutoridadOficio = []
    ResultadoOficio = []

    for x in products_list:
        for y in x:
            Nombre = y[0]
            NombreSolicitud.append(Nombre)
            RFC_00 = y[1] 
            RFC.append(RFC_00)
            Domicilio = y[2]
            DomicilioSolicitud.append(Domicilio)
            Oficio = y[3]
            NumerOficio.append(Oficio)
            Folio = y[4]
            NumeroFolio.append(Folio)
            Area = y[5]
            AreaOficio.append(Area)
            Autoridad = y[6]
            AutoridadOficio.append(Autoridad)
            Resultado = y[7]
            ResultadoOficio.append(Resultado)
            break

    Audit_dataframe = pd.DataFrame({
        'Nombre':NombreSolicitud,
        'RFC': RFC,
        'Dirección': DomicilioSolicitud,
        'Numero Oficio': NumerOficio,
        'Folio': NumeroFolio,
        'Area': AreaOficio,
        'Autoridad': AutoridadOficio,
        'Resultado': ResultadoOficio
         })

    return Audit_dataframe

AuditDataframe = CreateAuditDataFrame(dataframe)

def CreateAuditFiles(AuditDataframe):

    today = date.today()
    today = today.strftime("%m_%d_%y") 

    FileNamePNG = "SITIAA_%s.png"% today
    FileNameCSV = "SITIAA_%s.csv"% today

    path_PNG = os.path.join(FileNamePNG)
    path_CSV = os.path.join(FileNameCSV)
    AuditDataframe.dfi.export(path_PNG)
    AuditDataframe.to_csv(path_CSV)

def CreateTXT(AuditDataframe):

    name = AuditDataframe.Area
    name = np.unique(name.values)
    name = np.array_str(name)
    name = name[2:-2]

    file_name = "TXT_%s.txt"% name

    CompleteName = os.path.join(file_name)

    f = open(CompleteName, "w")

    AuditDataframeTXT =  AuditDataframe

    AuditDataframeGroup = AuditDataframeTXT.groupby(['Folio','Numero Oficio'])

    grouped_df = AuditDataframeGroup['Resultado']

    result = []

    for key, item in grouped_df:
        NumeroFolio = str(key[0])
        NumeroOficio = str(key[1]).strip()

        for i in item:
            if i == "SE ENCONTRO RESULTADO":
                for w in xml_paths:
                    try:
                        w.index(NumeroOficio)
                    except ValueError:
                        pass
                else:
                    result.append(NumeroOficio)

            elif i == "NO SE ENCONTRO RESULTADO":
                response = NumeroOficio + ',' + NumeroFolio + ',' + i + '\n' 
                f.write(response)
    f.close()
    print(result)

def PositiveResults(AuditDataframe):

    AuditDataframePR =  AuditDataframe

    AuditDataframeGroup = AuditDataframePR.groupby(['Folio','Numero Oficio','Nombre'])

    grouped_df = AuditDataframeGroup['Resultado']

    resultNumeroOficio = []
    resultXMLfile = []

    for key, item in grouped_df:
        NumeroFolio = str(key[0])
        NumeroOficio = str(key[1]).strip()
        NombreCliente = key[2]

        for i in item:
            if i == "SE ENCONTRO RESULTADO":
                resultNumeroOficio.append(NumeroOficio)

    for x in xml_paths:
        for i in resultNumeroOficio:
            o = i.replace("/", "-")
            if o in x:
                resultXMLfile.append(x)

    return resultXMLfile

ListPositiveResults = PositiveResults(AuditDataframe)

def MoveFoundFiles(TargetFolder):
    TargetFolder = '/Users/allan/desktop/SitiAA Python automatization'
    for x in ListPositiveResults:
        shutil.copy(x, TargetFolder)

#print(CreateAuditFiles(AuditDataframe))
#print(CreateTXT(AuditDataframe))
#print(MoveFoundFiles('/Users/allan/desktop/SitiAA Python automatization'))

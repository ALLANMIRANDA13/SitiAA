def ZipFilesPath(directory):
    zip_files_path = []
    for root, directories, files in os.walk(directory):
        for item in files:
            if item.endswith('.zip'):
                filepath = os.path.join(root, item)
                zip_files_path.append(filepath)
    return zip_files_path


def ExtractZipFiles(directory):
    folder = "Download Oficios"
    download_path = os.path.join(directory,folder)
    for i in ZipFilesPath(directory):
        with ZipFile(i,'r') as ZipObject:
            ZipObject.extractall(download_path)
    return download_path
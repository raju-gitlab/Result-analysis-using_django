import base64
import io
import os
from pathlib import Path
from numpy import size
import numpy as np
import pandas as pd
from django.core.files.storage import FileSystemStorage
from django.shortcuts import HttpResponse, redirect, render
from matplotlib import pyplot as plt
import seaborn as sb

# Create your views here.
BASE_DIR = Path(__file__).resolve().parent.parent
__login_user_Id = ""
__userlist = {'user': 'user', 'user@gmail.com': '1234567'}
__uploadedFiles = {

}
__global_df = any
__global_df_dataframes = {
    "dataset" : any
}

def index(request):
    return render(request, 'login.html')


def login(request):
    contxt = {"token": 0}
    contxt.update()
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('passkey')
        if __userlist.get(username) is None:
            contxt.update({'token': -1})
            return render(request, "login.html", contxt)
        else:
            if __userlist.get(username) == password:
                __login_user_Id = username
                return redirect('/home')
            else:
                contxt.update({'token': 0})
                return render(request, "login.html", contxt)
    else:
        contxt.update({'token': 1})
        return render(request, "login.html", contxt)


def register(request):
    if request.method == 'POST':
        username = request.POST.get('Email')
        passkey = request.POST.get('password')
        if __userlist.get(username) is not None:
            return HttpResponse("User already Exsits")
        else:
            __userlist[username] = passkey
        return redirect('login')
    else:
        return render(request, "register.html")


def homepage(request):
    contxt = {
        "token": 0
    }
    if request.method == "GET":
        return render(request, "userhome.html", contxt)


def upload(request):
    return render(request, "upload.html")


def uploaddatafiles(request):
    contxt = {
        "token": 1
    }
    file = any
    upload = request.FILES['uploadfile']
    acttualp = "media\\" + upload.name
    path =  os.path.join(BASE_DIR , acttualp)
    # filename = request.POST.get('filename')
    fss = FileSystemStorage()
    if os.path.exists(path):
        os.remove(path)
        file = fss.save(upload.name, upload)
    else:        
        file = fss.save(upload.name, upload)
    file_url = fss.url(file)
    return render(request, "userhome.html", contxt)


def uploaddata(request):
    contxt = {
        "token": 2
    }
    filename = request.POST.get('filename')
    filelocation = request.POST.get('filelink')
    __uploadedFiles[filename] = [__login_user_Id, filelocation]
    return render(request, "userhome.html", contxt)


def managedata(request):
    list_files = {}
    context = {
        "files": list_files,
        "templatedata": list_files,
        "i": 0
    }
    index = 0
    path = "E:\\Projects_Raju\\python\\Django\\analysis\\media"
    for i in os.listdir(path):
        filename = os.path.basename(i).split('/')[-1]
        pathoffile = path + filename
        context['files'][filename] = {
            "filename": filename, "pathoffile": pathoffile}
    for i in __uploadedFiles:
        context['files'][i] = {"filename": i,
                               "pathoffile": __uploadedFiles[i][1]}
    return render(request, "managedata.html", context)


def deletedataset(request):
    paramter = request.GET['Id']
    path = "E:\\Projects_Raju\\python\\Django\\analysis\\media\\" + paramter
    if os.path.exists(path):
        os.remove(path)
    else:
        __uploadedFiles.pop(paramter)
    return redirect('managedata')
def makegraph(request):
    paramter = request.GET['Id']
    listdata_set = {}   
    list_values = {
        "token_value" : 0,
        "Datasetname" : paramter,
        "loaded_data" : {},
        "nullcolumns" : {},
        "duplicatecolmns" : {},
        "nanvalues" : {},
        "columns" : {},
        "rowcount" : 0,
        "columncount" : 0,
        "totalduplicaterow" : 0,
        "graphs" : ["Distplot","Histplot","Scatterplot", "lineplot","Heatmap", "BarPlot", "PieChart"]
    }
    
    if(request.method == "GET"):
        path = "E:\\Projects_Raju\\python\\Django\\analysis\\media\\"+paramter
        if os.path.exists(path):
            path = "E:\\Projects_Raju\\python\\Django\\analysis\\media\\"+paramter
        else:
            path = paramter
        __global_df = pd.read_csv(path, index_col=False)
        __global_df_dataframes['dataset'] = pd.DataFrame(__global_df)
        dfn = __global_df.isnull().sum()
        _dfn = __global_df.isnull()
        dfd = __global_df.duplicated().sum()
        dfN = __global_df.notna().sum()
        data_html = __global_df.to_html()
        list_values['rowcount'] = len(__global_df.axes[0])
        list_values['columncount'] = len(__global_df.axes[1])
        list_values['totalduplicaterow'] = __global_df.duplicated().sum()
        list_values['loaded_data'] = data_html
        
        for i in _dfn:
            list_values['nullcolumns'][i] = {"Index" : i , "Value" : dfn[i]}
        for i in __global_df.columns:
            list_values['nanvalues'][i] = {"Index" : i , "Value" : dfN[i]}
        
        list_values["dataset"] = __global_df.to_string()
        list_values["duplicatecolmns"] = dfd
        list_values["columns"] = __global_df.columns.values
        return render(request, "analyzedata.html", list_values)
        
        
def checkuploads(request):
    list_values = {
        "diagrampath" : ""
    }
    paramter = request.GET['Id']
    path = "E:\\Projects_Raju\\python\\Django\\analysis\\media\\"+paramter
    if os.path.exists(path):
        path = "E:\\Projects_Raju\\python\\Django\\analysis\\media\\"+paramter
    else:
        path = paramter
    graph = request.POST.get('graph')
    xaxis = request.POST.get('xaxis')
    yaxis = request.POST.get('yaxis')
    
    df = pd.read_csv(path, index_col=False)
    # ["","", "","", "", ""]
    if graph == "Distplot":
        rdata = df[xaxis].values
        mdata = df[yaxis].values
        fig, ax = plt.subplots()
        sb.distplot([rdata, mdata], ax = ax)
        ax.set_xlim(1 , 200)
        plt.xlabel(xaxis)
        plt.ylabel(yaxis)
        plt.savefig(os.path.join(BASE_DIR, 'static\graphs\diagram'))
        list_values['diagrampath'] = '/static/graphs/diagram.png'
    if graph == "Histplot":
        sb.histplot([df[xaxis], df[yaxis]])
        plt.xlabel(xaxis)
        plt.ylabel(yaxis)
        plt.savefig(os.path.join(BASE_DIR, 'static\graphs\diagram'))
        list_values['diagrampath'] = '/static/graphs/diagram.png'
    if graph == "Scatterplot":
        sb.scatterplot([df[xaxis], df[yaxis]])
        plt.xlabel(xaxis)
        plt.ylabel(yaxis)
        plt.savefig(os.path.join(BASE_DIR, 'static\graphs\diagram'))
        list_values['diagrampath'] = '/static/graphs/diagram.png'
        #plot1
    if graph == "lineplot":
        sb.lineplot([df[xaxis], df[yaxis]])
        plt.xlabel(xaxis)
        plt.ylabel(yaxis)
        plt.savefig(os.path.join(BASE_DIR, 'static\graphs\diagram'))
        list_values['diagrampath'] = '/static/graphs/diagram.png'
    if graph == "Heatmap":
        sb.heatmap([df[xaxis], df[yaxis]])
        plt.xlabel(xaxis)
        plt.ylabel(yaxis)
        plt.savefig(os.path.join(BASE_DIR, 'static\graphs\diagram'))
        list_values['diagrampath'] = '/static/graphs/diagram.png'
    if graph == "BarPlot":
        sb.barplot([df[xaxis], df[yaxis]])
        plt.xlabel(xaxis)
        plt.ylabel(yaxis)
        plt.savefig(os.path.join(BASE_DIR, 'static\graphs\diagram'))
        list_values['diagrampath'] = '/static/graphs/diagram.png'
    if graph == "PieChart":
        data_array = df[xaxis].to_list()
        max_val = max(data_array)
        max_index = data_array.index(max_val)
        # explode_value = tuple([0 if i!=max_index else round((max_val/sum(data_array)),2) for i in range(len(data_array))])
        
        plt.pie(df[xaxis], autopct='%.0f%%')
        plt.savefig(os.path.join(BASE_DIR, 'static\graphs\diagram'))
        list_values['diagrampath'] = '/static/graphs/diagram.png'
    return render(request, "graphs.html", list_values)

def removecolumns(request):
    paramter = request.GET['Id']
    param = request.POST.get("fieldsnames")
    path = "E:\\Projects_Raju\\python\\Django\\analysis\\media\\" + paramter
    arraytages = param.split(',')
    df = pd.read_csv(path)
    abc = df.drop(arraytages, axis=1)
    os.remove(path)
    savepath = (os.path.join(path))
    abc.to_csv(path, index=False)
    return redirect("/analyze/?Id="+paramter)
def removenanornull(request):
    paramter = request.GET['Id']
    path = "E:\\Projects_Raju\\python\\Django\\analysis\\media\\" + paramter
    changetype = request.POST.get('posttype')
    df = pd.read_csv(path)
    if changetype == "Mean":
        for i in df.columns.values:
            meanvalue = df[i].mean()
            df[i].fillna(meanvalue, inplace=True)
    elif changetype == "Mod":
        for i in df.columns.values:
            meanvalue = df[i].mean()
            df[i].fillna(meanvalue, inplace=True)
    elif changetype == "Median":
        for i in df.columns.values:
            meanvalue = df[i].mean()
            df[i].fillna(meanvalue, inplace=True)
    else:
        df.dropna(inplace=True)
    os.remove(path)
    df.to_csv(path, index=False)
    return redirect("/analyze/?Id="+paramter)
def removeduplicate(request):
    paramter = request.GET['Id']
    path = "E:\\Projects_Raju\\python\\Django\\analysis\\media\\" + paramter
    df = pd.read_csv(path)
    df.drop_duplicates(inplace=True)
    os.remove(path)
    df.to_csv(path, index=False)
    return redirect("/analyze/?Id="+paramter)
def round(request):
    paramter = request.GET['Id']
    path = "E:\\Projects_Raju\\python\\Django\\analysis\\media\\" + paramter
    df = pd.read_csv(path)
    for i in df.columns.values:
        df[i] = df[i].apply(np.int64)
    os.remove(path)
    df.to_csv(path)
    return redirect("/analyze/?Id="+paramter)
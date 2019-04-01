#!/usr/bin/env python
# coding: utf-8

# In[28]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
from itertools import chain
#import seaborn as sns
import ffmpeg
import subprocess
import math
import gc
#import time
import sys


# In[102]:


if __name__ == '__main__':
    
    #--------------input--------------
    video_path = '/home/cognitive_task/trs/inp/trs.054/'
    csv_path = '/home/cognitive_task/make_video/15162_src1.csv'
    where_save = '/home/cognitive_task/pict/'
    access_rights = 0o755
    color_red = 50
    color_green = 5    
    which_id = [' CB062_2018-11-15T10:12:56.3761626+03:00_2']
    #read_and_changed(data, where_save, color_red, color_green, which_id)
    #pict2video(video_path, where_save)
    connect_all_video(where_save)
    


# In[101]:


#-----------getting csv, video and creating main folder:
def get_video(path):
    list_files = os.listdir(path)
    video = []
    for i in list_files:
        if 'central.avi' in i: 
            video.append(i)
    video.sort()
    return video

def convert2pict(start_pict, pict):
    cmds = ['ffmpeg', '-i', start_pict, pict]
    subprocess.Popen(cmds)
    
def convert2video(pict, video):
    cmds = ['ffmpeg', '-r', '12', '-y', '-i', pict, video]
    subprocess.Popen(cmds)

def read_csv(csv_path):
    try:
        data = pd.read_csv(csv_path)
        data = data.drop(557) # костыль
        return data
    except OSError:
        print('Cannot read csv, check your path')
        
def create_folder_with_all_photos(where_save, access_rights):
    try:  
        os.mkdir(where_save, access_rights)
    except OSError:  
        print ("Creation of the directory %s failed" % where_save)
    else:  
        print ("Successfully created the directory %s" % where_save)

#---------creating folders and video2pict-------------
def create_folders_and_video2pict(video_path, where_save, access_rights):
        names_video = get_video(video_path)
        #names_video = ['trs.054.0013.central.avi', '']
        for i in names_video:
            if len(i) > 1:
                i1 = i.split('.')
                i1 = i1[0:3]
                try:
                    save = ''
                    for j in i1:
                        save += j
                        save += '.'
                    os.mkdir(where_save + '/' + save[:-1], access_rights) 
                    os.mkdir(where_save + '/' + save[:-1] + '/' + 'right', access_rights)
                    os.mkdir(where_save + '/' + save[:-1] + '/' +  'down', access_rights)
                    os.mkdir(where_save + '/' + save[:-1] + '/' +'result', access_rights)
                except OSError:
                    print('Cannot create folder, sorry')
                convert2pict(video_path + save + 'central.avi', where_save + save[:-1] + '/' + save + '%6d.png')

                
#---------getting info about pictures in folders-------------
def get_info(path):
    list_files = os.listdir(path)
    files = []
    for i in list_files:
        i1 = i.split('.')  
        if len(i1) < 4:
            continue
        else:
            files.append(i1)
    return files

def sortFrame(info): 
    return info[3]  

def making_list_names():
    final_list = []
    list_files = os.listdir(where_save)
    list_files.sort()
    for pict in list_files:
        info = get_info(where_save + pict)
        
        for i in info:
            if (i[0] != 'trs'): 
                index = info.index(i)
                info.pop(index)
            i.pop(-1)
            if (i[-1] == 'png'):
                i.pop(-1)
            
        info.sort(key = sortFrame)
        final_list.append(info)
    return final_list


#---------reading pict, changing and saveing with graphics-------------

def read_and_changed(data, where_save, color_red, color_green, which_id):
    # ---------initialization-----------
    final_list = making_list_names()
    if which_id == '':
        data_objects = data['id_mar'].unique() # id_mar's
        data_objects = list(data_objects)
    else:
        data_objects = []
        data_objects.append(which_id)    
    objectsX = []
    objectsY = []
    objectsDist = []
    axes = 0
    objects_unique = [] 
    end = 0 # номер последней рамки в эпизоде
    # ---------
    for info in final_list: 
        print(len(info))
        for i in range(len(info)):            
            #gc.collect()
            #error = 0 # если по видео нет данных таблице - смена видео
            #exit = False # смена видео
            path_save = info[i][0] + '.' + info[i][1] + '.' + info[i][2] + '.' + info[i][3]
            path_for_graph = info[i][0] + '.' + info[i][1] + '.' + info[i][2]
            path = where_save + info[i][0] + '.' + info[i][1] + '.' + info[i][2] + '/' + path_save + '.png' 
            img = cv2.imread(path, cv2.IMREAD_COLOR)            
            cv2.putText(img, path_for_graph, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), 5)
            print(path)

            for j in data_objects:   
                serial = (data['serial'] == info[i][0])
                season = (data['season'] == int(info[i][1]))
                episode = (data['episode'] == int(info[i][2]))
                frame = (data['frame'] == int(info[i][3]) - 1)
                id_mar = (data['id_mar'] == j) # j - id_mar
                data_with_condition = data[serial & season & episode & frame & id_mar]
                ind = data[serial & season & episode & frame & id_mar].index
                print(ind)
                if not data_with_condition.empty:
                    if int(data_with_condition.id_det) == -1:
                        if j not in objects_unique:
                            objectsX.append([])
                            objectsY.append([])
                            objectsDist.append([])
                            objects_unique.append(j) # j - id_mar
                            axes += 1 # number of objects   
                        index_object = objects_unique.index(j)
                        objectsX[index_object].append(int(info[i][3]) + int(end))
                        objectsY[index_object].append(int(data_with_condition.hei_mar))
                        objectsDist[index_object].append(10000)                           
                        if int(info[i][3]) == len(info):
                            
                            end += len(info) 

                        cv2.putText(img,'Obj #' + str(index_object + 1), (int(data_with_condition.x_mar), int(data_with_condition.y_mar) - 20),
                                     cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)

                        cv2.rectangle(img, (int(data_with_condition.x_mar), int(data_with_condition.y_mar)), 
                                      (int(data_with_condition.x_mar) + int(data_with_condition.wid_mar),
                                       int(data_with_condition.y_mar) + int(data_with_condition.hei_mar)), (0, 0, 255), 5)
                        cv2.imwrite(path, img)


                    else: 
                        dist = float(data_with_condition.dist.item().replace(',','.'))
                        if dist <= color_red: # dist_max = 5     
                            if dist <= color_green:
                                if j not in objects_unique:
                                    objectsX.append([])
                                    objectsY.append([])
                                    objectsDist.append([])
                                    objects_unique.append(j) # j - id_mar
                                    axes += 1 # number of objects
                                index_object = objects_unique.index(j)
                                objectsX[index_object].append(int(info[i][3]) + int(end))
                                objectsY[index_object].append(int(data_with_condition.hei_mar))
                                objectsDist[index_object].append(dist)   
                                   
                                if int(info[i][3]) == len(info):
                                    end += len(info) 

                                cv2.putText(img,'Obj #' + str(index_object + 1), (int(data_with_condition.x_mar), int(data_with_condition.y_mar) - 20),
                                         cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)

                                cv2.rectangle(img, (int(data_with_condition.x_mar), int(data_with_condition.y_mar)), 
                                          (int(data_with_condition.x_mar) + int(data_with_condition.wid_mar),
                                           int(data_with_condition.y_mar) + int(data_with_condition.hei_mar)), (255, 255, 255), 5)
                                cv2.rectangle(img, (int(data_with_condition.x_det), int(data_with_condition.y_det)), 
                                          (int(data_with_condition.x_det) + int(data_with_condition.wid_det),
                                           int(data_with_condition.y_det) + int(data_with_condition.hei_det)), (0, 255, 0), 4)
                                cv2.imwrite(path, img)  
                                
                            else:
                                if j not in objects_unique:
                                    objectsX.append([])
                                    objectsY.append([])
                                    objectsDist.append([])
                                    objects_unique.append(j) # j - id_mar
                                    axes += 1 # number of objects
                                index_object = objects_unique.index(j)
                                objectsX[index_object].append(int(info[i][3]) + int(end))
                                objectsY[index_object].append(int(data_with_condition.hei_mar))
                                objectsDist[index_object].append(dist)   
                                   
                                if int(info[i][3]) == len(info) :
                                    end += len(info) 

                                cv2.putText(img,'Obj #' + str(index_object + 1), (int(data_with_condition.x_mar), int(data_with_condition.y_mar) - 20),
                                         cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)

                                cv2.rectangle(img, (int(data_with_condition.x_mar), int(data_with_condition.y_mar)), 
                                          (int(data_with_condition.x_mar) + int(data_with_condition.wid_mar),
                                           int(data_with_condition.y_mar) + int(data_with_condition.hei_mar)), (255, 255, 255), 5)
                                cv2.rectangle(img, (int(data_with_condition.x_det), int(data_with_condition.y_det)), 
                                          (int(data_with_condition.x_det) + int(data_with_condition.wid_det),
                                           int(data_with_condition.y_det) + int(data_with_condition.hei_det)), (0, 255, 255), 4)
                                cv2.imwrite(path, img)

                        else: 
                            if j not in objects_unique:
                                objectsX.append([])
                                objectsY.append([])
                                objectsDist.append([])
                                objects_unique.append(j) # j - id_mar
                                axes += 1 # number of objects
                            index_object = objects_unique.index(j)
                            objectsX[index_object].append(int(info[i][3]) + int(end))
                            objectsY[index_object].append(int(data_with_condition.hei_mar))
                            objectsDist[index_object].append(dist)                               
                            if int(info[i][3]) == len(info):
                                end += len(info) 
                            
                            cv2.putText(img,'Obj #' + str(index_object + 1), (int(data_with_condition.x_mar), int(data_with_condition.y_mar) - 20),
                                     cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)

                            cv2.rectangle(img, (int(data_with_condition.x_mar), int(data_with_condition.y_mar)), 
                                      (int(data_with_condition.x_mar) + int(data_with_condition.wid_mar),
                                       int(data_with_condition.y_mar) + int(data_with_condition.hei_mar)), (0, 0, 255), 5)
                            cv2.rectangle(img, (int(data_with_condition.x_det), int(data_with_condition.y_det)), 
                                      (int(data_with_condition.x_det) + int(data_with_condition.wid_det),
                                       int(data_with_condition.y_det) + int(data_with_condition.hei_det)), (255, 255, 255), 5)
                            cv2.imwrite(path, img)
                            
            #----------draw graphics------------
            down_graph(axes, objectsX, objectsY, objectsDist, path_save, where_save, path_for_graph, color_red, color_green)
            right_graph(axes, objectsY, objectsDist, path_save, where_save, path_for_graph, color_red, color_green)
        
                

#-------------painting graphics with saving in folders-----------

def set_size(w,h, ax=None):
    """ w, h: width, height in inches """
    if not ax: ax=plt.gca()
    l = ax.figure.subplotpars.left
    r = ax.figure.subplotpars.right
    t = ax.figure.subplotpars.top
    b = ax.figure.subplotpars.bottom
    figw = float(w)/(r-l)
    figh = float(h)/(t-b)
    ax.figure.set_size_inches(figw, figh)

def down_graph(axes, objectsX, objectsY, objectsDist, path_save, where_save, path_for_graph, color_red, color_green):
    fig, ax = plt.subplots(1, axes)
    fig.subplots_adjust(wspace=0.4, bottom = 0.2)
    j = 0
    if axes > 1:
        for i in ax:       
            i.set_xlim(0, 1100)
            i.set_ylim(0, 400)
            i.tick_params(axis = 'both', which = 'major', labelsize = 7)
            for k in range(len(objectsX[j])):
                if objectsDist[j][k] <= color_red: 
                    if objectsDist[j][k] <= color_green:
                        i.scatter(objectsX[j][k], objectsY[j][k], marker = 'o', color = 'green', s=30)
                    else:
                        i.scatter(objectsX[j][k], objectsY[j][k], marker = 'o', color = 'yellow', s=30)                    
                else: 
                    i.scatter(objectsX[j][k], objectsY[j][k], marker = 'o', color = 'red', s=30)   
        
            j += 1
            i.set_title('Object #' + str(j))
        
        ax[0].set_ylabel("Height", fontsize=13)
        ax[0].set_xlabel("Number of frame", fontsize=13)
        
    else:
        ax.set_xlim(0, 1100)
        ax.set_ylim(0, 400)
        ax.tick_params(axis = 'both', which = 'major', labelsize = 7)
        ax.set_ylabel("Height", fontsize=13)
        ax.set_xlabel("Number of frame", fontsize=13)
        for k in range(len(objectsX[j])):
            if objectsDist[j][k] <= color_red: 
                if objectsDist[j][k] <= color_green:
                    ax.scatter(objectsX[j][k], objectsY[j][k], marker = 'o', color = 'green', s=30)
                else:
                    ax.scatter(objectsX[j][k], objectsY[j][k], marker = 'o', color = 'yellow', s=30)                    
            else: 
                ax.scatter(objectsX[j][k], objectsY[j][k], marker = 'o', color = 'red', s=30)
        
        j += 1
        ax.set_title('Object #' + str(j))
        
    set_size(1920/(96*4), 1080/(96*4))
    
    plt.savefig(where_save  + path_for_graph + '/down/' + path_save + '.png', dpi = 200)
    graphic_final = cv2.imread(where_save  + path_for_graph + '/down/' + path_save + '.png', cv2.IMREAD_COLOR)  
    img = cv2.imread(where_save  + path_for_graph + '/' + path_save + '.png', cv2.IMREAD_COLOR)
    graphic_final = cv2.resize(graphic_final, (1920,700), interpolation = cv2.INTER_AREA)
    vis = np.concatenate((img, graphic_final), axis=0)
    cv2.imwrite(where_save  + path_for_graph + '/' + path_save + '.png', vis)
    plt.close(fig)
        
def right_graph(axes, objectsY, objectsDist, path_save, where_save, path_for_graph, color_red, color_green):
    fig, ax = plt.subplots(axes, 1)
    fig.subplots_adjust(top = 0.9, wspace = 0, hspace = 0.6)
    j = 0 
    if axes > 1:        
        for i in ax:  
            #gc.collect()
            i.set_xlim(0, 1)
            i.set_ylim(0, 400)
            i.tick_params(axis = 'both', which = 'major', labelsize = 7)
            for k in range(len(objectsDist[j])): 
                if objectsDist[j][k] <= color_red:
                    if objectsDist[j][k] <= color_green:
                        i.scatter(1/(1 + math.log(objectsDist[j][k] + 1)), objectsY[j][k], marker = 'o', color = 'green', s = 30)
                    else: 
                        i.scatter(1/(1 + math.log(objectsDist[j][k] + 1)), objectsY[j][k], marker = 'o', color = 'yellow', s = 30)
                else:
                    if objectsDist[j][k] == 10000:
                        i.scatter(0, objectsY[j][k], marker = 'o', color = 'red', s = 30)
                    else: 
                        i.scatter(1/(1 + math.log(objectsDist[j][k] + 1)), objectsY[j][k], marker = 'o', color = 'red', s = 30)
     
                
                if k != 0:
                    if objectsDist[j][k-1] <= color_red:
                        if objectsDist[j][k-1] <= color_green:
                            i.scatter(1/(1 + math.log(objectsDist[j][k-1] + 1)), objectsY[j][k-1], marker = 'o', color = 'green', s = 30)
                        else: 
                            i.scatter(1/(1 + math.log(objectsDist[j][k-1] + 1)), objectsY[j][k-1], marker = 'o', color = 'yellow', s = 30)
                    else:
                        if objectsDist[j][k-1] == 10000:
                            i.scatter(0, objectsY[j][k-1], marker = 'o', color = 'red', s = 30)
                        else: 
                            i.scatter(1/(1 + math.log(objectsDist[j][k-1] + 1)), objectsY[j][k-1], marker = 'o', color = 'red', s = 30)
                if objectsDist[j][k] == 10000:
                    i.scatter(0, objectsY[j][k], marker = 'o', color = 'pink', s = 30) 
                else: 
                    i.scatter(1/(1 + math.log(objectsDist[j][k] + 1)), objectsY[j][k], marker = 'o', color = 'pink', s = 30)
                
                
            
            j += 1
            i.set_title('Object #' + str(j))
        ax[-1].set_ylabel("HeigHt", fontsize=10)
        ax[-1].set_xlabel("Confidence", fontsize=10)
        
    else:           
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 400)
            ax.tick_params(axis = 'both', which = 'major', labelsize = 7)
            ax.set_ylabel("HeigHt", fontsize=10)
            ax.set_xlabel("Confidence", fontsize=10)
            for i in range(len(objectsDist[j])):
                #gc.collect()     
                if objectsDist[j][i] <= color_red:
                    if objectsDist[j][i] <= color_green:
                        ax.scatter(1/(1 + math.log(objectsDist[j][i] + 1)), objectsY[j][i], marker = 'o', color = 'green', s = 30)
                    else: 
                        ax.scatter(1/(1 + math.log(objectsDist[j][i] + 1)), objectsY[j][i], marker = 'o', color = 'yellow', s = 30)
                else:
                    if objectsDist[j][i] == 10000:
                        ax.scatter(0, objectsY[j][i], marker = 'o', color = 'red', s = 30)
                    else: 
                        ax.scatter(1/(1 + math.log(objectsDist[j][i] + 1)), objectsY[j][i], marker = 'o', color = 'red', s = 30)
                
                if i != 0:
                    if objectsDist[j][i-1] <= color_red:
                        if objectsDist[j][i-1] <= color_green:
                            ax.scatter(1/(1 + math.log(objectsDist[j][i-1] + 1)), objectsY[j][i-1], marker = 'o', color = 'green', s = 30)
                        else: 
                            ax.scatter(1/(1 + math.log(objectsDist[j][i-1] + 1)), objectsY[j][i-1], marker = 'o', color = 'yellow', s = 30)
                    else:
                        if objectsDist[j][i-1] == 10000:
                            ax.scatter(0, objectsY[j][i-1], marker = 'o', color = 'red', s = 30)
                        else: 
                            ax.scatter(1/(1 + math.log(objectsDist[j][i-1] + 1)), objectsY[j][i-1], marker = 'o', color = 'red', s = 30)
                if objectsDist[j][i] == 10000:
                    ax.scatter(0, objectsY[j][i], marker = 'o', color = 'pink', s = 30) 
                else: 
                    ax.scatter(1/(1 + math.log(objectsDist[j][i] + 1)), objectsY[j][i], marker = 'o', color = 'pink', s = 30) 
                
                
            j += 1
            ax.set_title('Object #' + str(j))
            
            
    set_size(1500/(96*4), 2000/(96*4))
    
    plt.savefig(where_save  + path_for_graph + '/right/' + path_save + '.png', dpi = 200)
    graphic_final = cv2.imread(where_save  + path_for_graph + '/right/' + path_save + '.png', cv2.IMREAD_COLOR) 
    img = cv2.imread(where_save  + path_for_graph + '/' + path_save + '.png', cv2.IMREAD_COLOR)
    graphic_final = cv2.resize(graphic_final, (1920,1780), interpolation = cv2.INTER_AREA)
    vis = np.concatenate((img, graphic_final), axis = 1)
    cv2.imwrite(where_save  + path_for_graph + '/' + path_save + '.png', vis)
    plt.close(fig)

    
#---------creating folders and video2pict-------------
def pict2video(video_path, where_save):    
    names_video = get_video(video_path)
    for i in names_video:
        if len(i) > 1:
            i1 = i.split('.')
            i1 = i1[0:3]
            save = ''
            for j in i1:
                save += j
                save += '.'
            convert2video(where_save + save[:-1] + '/' + save + '%6d.png',
                          where_save  + save[:-1] + '/' +'result' + '/' + save + 'central.avi')
            
            if ('linux' in get_platform()) or ('Linux' in get_platform()):
                 os.popen('cp ' +  where_save  + save[:-1] + '/' + 'result' + '/' + save + 'central.avi' + ' ' + where_save + save + 'central.avi')
            
            else:
                 os.popen('copy ' +  where_save  + save[:-1] + '/' + 'result' + '/' + save + 'central.avi' + ' ' + where_save + save + 'central.avi')

#------------------connect all video---------------                                        
def get_info_final(path):
    list_files = os.listdir(path)
    files = []
    for i in list_files:
        if '.avi' in i:
            files.append(i)
    files.sort()
    return files


def connect_all_video(where_save):
    lists = get_info_final(where_save)
    string = 'cat '
    for i in lists[4:12]:
        string += where_save + i
        string += ' '
    string += '> '
    string += where_save + 'pre.avi'
    os.popen(string)
    print('mencoder -forceidx -oac copy -ovc copy' + where_save + 'pre.avi -o' + where_save + 'result.avi')
    os.popen('mencoder -forceidx -oac copy -ovc copy ' + where_save + 'pre.avi -o ' + where_save + 'result.avi')



def get_platform():
    platforms = {
        'linux1' : 'Linux',
        'linux2' : 'Linux',
        'darwin' : 'OS X',
        'win32' : 'Windows'
    }
    if sys.platform not in platforms:
        return sys.platform
    
    return platforms[sys.platform]
    


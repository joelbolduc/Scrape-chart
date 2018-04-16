# -*- coding: utf-8 -*-
"""
Created on Sun Apr 15 15:40:48 2018

@author: Joel
"""

from scipy.misc import imread as read
from scipy.misc import imsave as write
import numpy as np

def dist(col1,col2):
    #distance between two rgb colors
    s=0
    for i in range(len(col1)):
        s+=abs(col1[i]-col2[i])
    return s

def avg_col(ar):
    #average color of an image or a line in an image
    #two cases depending on number of dimensions of the array
    if(ar.ndim==2):
        col=np.array(list([0.0]*3))
        for i in range(len(ar)):
            col+=ar[i]
        col/=len(ar)
        return col
    elif(ar.ndim==3):
        col=np.array(list([0.0]*3))
        for i in range(len(ar)):
            for j in range(len(ar[i])):
                col+=ar[i][j]
        col/=(len(ar)*len(ar[i]))
        return col

def get_satur(image):
    #simply creates a saturation image from original image
    #saturation of a color is computed as max(r,g,b)-min(r,g,b)
    img=image
    out=[]
    for i in range(len(img)):
        lne=[]
        for j in range(len(img[0])):
            col=[]
            for k in range(3):
                xp=min(i+1,len(img)-1)
                xx=i
                yp=min(j+1,len(img[0])-1)
                yy=j
                col.append(abs(float(img[xp][yy][k])-2*float(img[xx][yy][k])+float(img[xx][yp][k])))
            r=(max(col)-min(col))
            lne.append(r)
        out.append(lne)
    out=np.array(out)
    return out/np.max(out)

def get_value(img,line):
    val1=None
    val2=None
    for i in range(len(img)):
        if(img[i][line]>0.2 and val1==None):
            val1=i
        elif(img[i][line]>0.2 and val2==None and (i>val1+35 or i>0.85*len(img))):
            val2=i
            break
    if(val1==None):
        return None
    if(val2==None):
        y=len(img)-val1
    else:
        y=val2-val1
    return [line,y]

def get_values(image,x_min,x_max,x_log,y_min,y_max,y_log):
    #image is the original image
    #x_min, x_max, y_min and y_max are the minimum and maximum values of the axes
    #notice that this is not the maximum and minimum displayed on the axes
    #but the maximum and minimum actually achieved by the function
    #x_log and y_log are boolean values indicating if the axis follows a logarithmic scale
    #if the variable is False, linear scale is assumed
    img=read(image)
    #converts a bmp image of a chart (such as GDP over time)
    #into a list of [x,y] couples representing the data on said chart
    col=avg_col(img)
    #average color of the image. Usefull to distinguish backgorund from meaningfull information
    cols=[]
    for i in range(len(img)):
        for j in range(len(img)):
            cols.append(np.max(np.abs(img[i][j]-col)))
    cols=np.array(cols)
    p=(np.percentile(cols,98))
    #Creates list of colors and their level of deviation from background color
    #Uses this list to calculate 98th percentile.
    #This has been empirically shown to be a good percentile to seperate background from
    #the data function
    for i in range(len(img)):
        for j in range(len(img[i])):
            if(np.max(np.abs(img[i][j]-col))>p):
                img[i][j]=[255,0,0]
            else:
                pass
    #All points that represent a data point (that have above 98th percentile deviation from background)
    #are colored red in order to be picked out by the rest of the algorithm
    image=img
    out=get_satur(image)
    #calculates saturation at each point.
    #Since function is often colored, get_satur would pick up on it.
    #If it is not, the added red allows get_satur to do it's job
    #If it is colors, the benefits of saturation and percentile add up
    out2=[]
    for i in range(len(out)):
        lne=[]
        for j in range(len(out[i])):
            xm=max(j-2,0)
            xp=min(j+3,len(out[i])-1)
            lne.append(np.mean(out[i][xm:xp]))
        out2.append(lne)
    out=out2
    #Image is blurred out a little bit
    #in order to avoid gaps in data due to imperfect image
    values=[]
    strech_beginnings=[]
    strech_ends=[]
    #since text on the side of graph will also register as function with this algorithm
    #(thanks to high percentile value), this text will be seperated from function
    #using the fact that, if detected data is split up in several chunks,
    #the largest one is most likely to be the actual function
    #Therefore, this code creates a list of blocks of contiguous data along with it's
    #beginning and end, and then picks out the longest one, and considers it to be the data
    in_strech=False
    for i in range(len(out[0])):
        g=(get_value(out,i))
        if(g!=None and not in_strech):
            in_strech=True
            strech_beginnings.append(i)
        if(g==None and in_strech):
            in_strech=False
            strech_ends.append(i)
        values.append(g)
    if(in_strech):
        strech_ends.append(len(out))
    strech_lengths=[]
    for i in range(len(strech_beginnings)):
        strech_lengths.append(strech_ends[i]-strech_beginnings[i])
    M=max(strech_lengths)
    ind=strech_lengths.index(M)
    beg=strech_beginnings[ind]
    end=strech_ends[ind]
    #Fisrt and last 4 values are croped off the avoid problems due to
    #discontinuity of drawing near the edges
    end-=4
    beg+=4
    if(beg>=end):
        end=beg
    #keeping at least one data point if the graph is very small
    v=values[beg:end]
    #here, we are going to compute minimum and maximum values for both axis.
    #based on values given to the function, they will then be scaled up to the actual values
    vx=[]
    vy=[]
    for i in range(len(v)):
        vx.append(v[i][0])
        vy.append(v[i][1])
    min_x=min(vx)
    max_x=max(vx)
    min_y=min(vy)
    max_y=max(vy)
    #two types of formulas based on value of x_log and y_log
    #this variable indicates if an axis follows a logarithmic scale
    for i in range(len(v)):
        vx[i]=(vx[i]-min_x)/(max_x-min_x)
        vy[i]=(vy[i]-min_y)/(max_y-min_y)
        if(x_log==False):
            vx[i]=(x_max-x_min)*vx[i]+x_min
        else:
            vx[i]=x_min*pow(x_max/x_min,vx[i])
        if(y_log==False):
            vy[i]=(y_max-y_min)*vy[i]+y_min
        else:
            vy[i]=y_min*pow(y_max/y_min,vy[i])
        v[i]=[vx[i],vy[i]]
    return v
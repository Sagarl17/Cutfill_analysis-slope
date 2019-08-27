import os
import cv2
import sys
import json
import math
import gdal
import numpy as np
from solaris import *
import multiprocessing
from pyproj import Proj, transform
from shapely.geometry import Point,LineString
from shapely.geometry.polygon import Polygon


sys.setrecursionlimit(10000000)

#Adding filenames to the program as arguments.
#filename1 is dtm tif file
#filename 2 is json file for boundaries of area.
#filename 3 is base station height 

filename = str(sys.argv[1])
filename2= str(sys.argv[2])
base_station_ht = float(sys.argv[3])

def check_direction(coord,Direction):
    transformed=[]
    for  i in coord:
        inProj = Proj(init='epsg:32644')
        outProj = Proj(init='epsg:4326')
        x,y = transform(inProj,outProj,i[0],i[1])
        transformed.append([y,x])

    st=[]
    start=[]

    dirx=""
    diry=""
    for i in range(len(transformed)-1):
        dx=transformed[i+1][0]-transformed[i][0]
        dy=transformed[i+1][1]-transformed[i][1]
        if dx>0:
            dirx=str("North")
        elif dx<0:
            dirx=str("South")
        if dy>0:
            diry=str("East")
        elif dy<0:
            diry=str("West")
        direction=dirx+diry
        if direction==Direction:
            st.append([transformed[i][1],transformed[i][0]])
    transformed = transformed[::-1]

    for i in range(len(transformed)-1):
        dx=transformed[i+1][0]-transformed[i][0]
        dy=transformed[i+1][1]-transformed[i][1]
        if dx>0:
            dirx=str("North")
        elif dx<0:
            dirx=str("South")
        if dy>0:
            diry=str("East")
        elif dy<0:
            diry=str("West")
        direction=dirx+diry
        if direction==Direction:
            st.append([transformed[i][1],transformed[i][0]])
    
    for  i in st:
        inProj = Proj(init='epsg:4326')
        outProj = Proj(init='epsg:32644')
        x,y = transform(inProj,outProj,i[0],i[1])
        start.append([x,y])
    
    return start





class featurecalculation:
    def features(self,filename):
        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
        result=pool.map(self.calc, range(division),chunksize=1)

        #Sorting data for each worker process from multiprocessing data array
        for divo in range(division):
            cut_polygons = result[divo][2]
            fill_polygons = result[divo][3]
        
        #Organizing data as required for our required output
            for i in range(len(cut_polygons)):
                feature = {}
                feature["type"] = "Feature"
                feature["properties"] = {}
                feature["geometry"] = {}
                cut_polygon_coords =[]
                cut_polygon = cut_polygons[i]
                x, y = cut_polygon.exterior.coords.xy
                for i in range(len(x)):
                    cut_polygon_coords.append([x[i],y[i]])
                feature["properties"]["name"] = names[divo]
                feature["properties"]["type"] = "cut"
                feature["properties"]["color"] = "#ff0000"
                feature["properties"]["volume"] = "cut volume : "+str(result[divo][0])+" m^3"
                feature["properties"]["area"] = "cut area : "+str(cut_polygon.area)+" m^2"
                feature["properties"]["total_area"] = "total area : "+str(result[divo][4])+" m^2"
                feature["geometry"]["type"] = "Polygon"
                feature["geometry"]["coordinates"] =[]
                feature["geometry"]["coordinates"].append(cut_polygon_coords)
                arr.append(feature)

            for i in range(len(fill_polygons)):
                feature = {}
                feature["type"] = "Feature"
                feature["properties"] = {}
                feature["geometry"] = {}
                fill_polygon_coords =[]
                fill_polygon = fill_polygons[i]
                x, y = fill_polygon.exterior.coords.xy
                for i in range(len(x)):
                    fill_polygon_coords.append([x[i],y[i]])
                feature["properties"]["name"] = names[divo]
                feature["properties"]["type"] = "fill"
                feature["properties"]["color"] = "#00cc00"
                feature["properties"]["volume"] = "fill volume : "+str(result[divo][1])+" m^3"
                feature["properties"]["area"] = "fill area : "+str(fill_polygon.area)+" m^2"
                feature["properties"]["total_area"] = "total area : "+str(result[divo][4])+" m^2"
                feature["geometry"]["type"] = "Polygon"
                feature["geometry"]["coordinates"] =[]
                feature["geometry"]["coordinates"].append(fill_polygon_coords)
                arr.append(feature)

        final_arr = {}
        final_arr["type"] = "FeatureCollection"
        final_arr["features"] = arr


        # Wring ata to json file

        with open("slope_output.json", "w") as outfile:
            json.dump(final_arr, outfile)

    def calc(self,div):
        print("Worker process started:",div)
        base_height= base_heights[int(div)]
        slope=slopes[int(div)]
        direction=directions[int(div)]
        block = coordinates[int(div)]
        my_cord = block[0]
        start=check_direction(my_cord,direction)
        start_line=LineString(start)
        polygon = Polygon(my_cord)
        x_array=[]
        y_array=[]
        cut=[]
        fill = []
        for i in range(len(block[0])):
            x_array.append(block[0][i][0])
            y_array.append(block[0][i][1])
        x_min_geo = (min(x_array)-geo_trans[0])/geo_trans[1]
        y_min_geo = (min(y_array)-geo_trans[3])/geo_trans[5]
        x_max_geo = (max(x_array)-geo_trans[0])/geo_trans[1]
        y_max_geo = (max(y_array)-geo_trans[3])/geo_trans[5]
        x_min_geo = int(x_min_geo - 20)
        x_max_geo = int(x_max_geo + 20)
        y_min_geo = int(y_min_geo - 20)
        y_max_geo = int(y_max_geo + 20)

        cut_x=[]
        cut_y=[]
        fill_x=[]
        fill_y=[]

        image=np.zeros((rows,cols,3))

        for e in range(x_min_geo, x_max_geo):
            for f in range(y_max_geo,y_min_geo):
                X = geo_trans[0] + e*geo_trans[1] + f*geo_trans[2]  # base+ width*gsd
                Y = geo_trans[3] + e*geo_trans[4] + f*geo_trans[5]  # base + height*gsd
                point = Point(X, Y)
                elv = elevation[f,e]
                if point.within(polygon) == True:
                    ld=start_line.distance(point)
                    base_height_needed=base_height+(slope*ld)
                    if elv > base_height_needed :
                        cut.append(elv - base_height_needed)
                        image[f,e]=[0,0,255]
                    elif elv < base_height_needed :
                        fill.append(base_height_needed - elv)
                        image[f,e]=[0,255,0]

        image=image[...,::-1]

        mask2poly = vector.mask.mask_to_poly_geojson(image, channel_scaling=[1,-1,-1], bg_threshold=100, simplify=True,tolerance=5)
        out_red = vector.polygon.georegister_px_df(mask2poly, affine_obj=geo_trans, crs='epsg:32643')

        mask2poly = vector.mask.mask_to_poly_geojson(image, channel_scaling=[-1,1,-1], bg_threshold=100, simplify=False,tolerance=5)
        out_green = vector.polygon.georegister_px_df(mask2poly, affine_obj=geo_trans, crs='epsg:32643')
        
        fill_poly=out_green["geometry"]
        cut_poly=out_red["geometry"]
        cut_sum= sum(cut)
        fill_sum = sum(fill)
        cut_vol = cut_sum *gsd*gsd
        fill_vol = fill_sum *gsd*gsd
        print("Worker done:",div)
        print(names[div])
        print("Cut Volume:",cut_vol)
        print("Fill Volume:",fill_vol)
        print(len(cut_poly))
        print(len(fill_poly))
        return cut_vol,fill_vol,cut_poly,fill_poly,polygon.area

# if not(os.path.exists(filename+"_data.json")):
ds = gdal.Open(filename)
band = ds.GetRasterBand(1)
elevation = band.ReadAsArray()
# print(band
cols=ds.RasterXSize
rows=ds.RasterYSize
geo_trans = ds.GetGeoTransform()
gsd=geo_trans[1]
arr = []
evalv = []
n=0
c=0

block =[]
coordinates=[]
names=[]
base_heights = []
directions=[]
slopes=[]
input_file = open (filename2)
my_json = json.load(input_file)

#sorting data as required for our calculations
f=my_json["features"]
for h in f:
    g=(h["geometry"])
    p=g["coordinates"]
    n=h["properties"]
    name=n["Name"]
    height = n["height"] + base_station_ht
    base_heights.append(height)
    names.append(name)
    if "slope" in n:
        slopes.append(n["slope"])
    elif "angle" in n:
        slopes.append(math.tan(n["angle"]))

    directions.append(n["direction"])
    coordinates.append(p)
division=len(coordinates)
fe=featurecalculation()
fe.features(filename)

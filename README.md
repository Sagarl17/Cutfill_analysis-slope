# Cutfill_analysis-slope

Installation instructions:
There are multiple library dependencies for the python code such as:

GDAL==2.4.0

geojson==2.5.0

numpy==1.17.0

opencv-python==4.1.0.25

opencv-python-headless==4.1.0.25

pyproj==2.2.1

Shapely==1.6.4.post2

You need to install these with 'pip install -r requirements.txt' before you can run the code


Download additional folder named "Solaris" from the following link and place the folder in the main folder:
https://drive.google.com/drive/folders/134vCFpQtOM4TLYgfkyyYEamkvlAJMIvd?usp=sharing

An example tif file is provided via the following link and replace the dtm.tif file in the main folder with the example tif file to test the code:
https://drive.google.com/file/d/1MVmC5rdCYfqWP4eMKEOEENIK7T_45MEb/view?usp=sharing

Cut fill analysis if sloped surfaces are required 
Usage : 

a) If the angle or slope is provided:
    python -W ignore cutfill_slope.py dtm.tif block_bounds.json base_height of station


    cutfill_slope calculates the cut fill of sloping sites given that the angle or slope of the site is provided

    dtm.tif is the dtm file for the site
    block_bounds.json is the json file containing all polygons with their slopes or angles (in properties)
    base_height of station is the height of station from which measurements were made. This is floating number

b) If elevation is provided:
    python -W ignore cutfill_elevation.py dtm.tif block_bounds.json base_height of station


    cutfill_slope calculates the cut fill of sloping sites given that the angle or slope of the site is provided

    dtm.tif is the dtm file for the site
    block_bounds.json is the json file containing all polygons with their slopes or angles (in properties)
    base_height of station is the height of station from which measurements were made. This is floating number

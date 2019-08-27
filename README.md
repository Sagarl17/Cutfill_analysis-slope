# Cutfill_analysis-slope
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

# Scrape-chart
This file contains a function that takes in a visual chart in bmp format (such as gdp over time) and returns a list of (x,y) pairs representing the data. Scaling information must be inputed manually (min and max of each axis, and weather the axis has a logarthmic scale or not). In a future version, conversion to csv file will be added.
Title should be cropped out of the image, otherwise, the alorithm might confuse the text as being part of the curve, leading to unexoected results.

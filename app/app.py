from flask import Flask, render_template, redirect, url_for, request, Response
from flask import make_response
import os.path
import requests as r
import cv2
from backend.utils import image_to_string
from backend.maps_query import gmaps_image, gmaps_area
from backend.segmentation import image_segmentation
from backend.solarPanelClass import solarPanel
import base64

app = Flask(__name__)
NEWS_API_KEY = '--'
DIFFBOT_TOKEN = '--'

@app.route("/")
def home():
    return render_template("index.html", title = 'Solar Rooftops')

@app.route("/index")
def index():
    return render_template("index.html", title = 'Solar Rooftops')

@app.route('/run_address', methods=['GET', 'POST'])
def run_address():
    if request.method == 'POST':
        address = request.form['address']

        image = gmaps_image(address)
        sat_buff = image_to_string(image)

        segmented_image, area_percent = image_segmentation(image)
        total_area, latitude, longitude = gmaps_area(address)
        area_in_square_meters = total_area*area_percent
        seg_buff = image_to_string(segmented_image)

        # Actually use the solar panel information
        solar_panel = solarPanel(address, latitude, longitude, 0.25*area_in_square_meters)
        mean_light_intensity = solar_panel.meanLightIntensity
        montly_savings = solar_panel.monthlySaving

        resp = make_response('{"address" : "' + address + '", "sat_img" : "' + sat_buff + '", "seg_img" : "' + seg_buff + \
            '", "area" : "' + "%.2f" % area_in_square_meters + '", "mean_light_intensity" : "' +  "%.2f" % mean_light_intensity + \
            '", "montly_savings" : "' + "%.2f" % montly_savings + '"}')
        resp.headers['Content-Type'] = "application/json"
        return resp

if __name__ == "__main__":
    app.run(debug = True)

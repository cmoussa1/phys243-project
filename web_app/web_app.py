
# PHYS-243
# University of California, Riverside
# Final Project
# Author: James Siefert

# To view the app, run this file and then visit the local url (http://127.0.0.1:5000)

from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge
from io import BytesIO
import base64
import os

from utility import cost_distribution_estimate_non_mp_version, cost_distribution_estimate

import warnings



warnings.simplefilter("ignore", category=UserWarning)

app = Flask("Cost Distribution")

script_dir = os.path.dirname(os.path.abspath(__file__))


def predict_home_price(bedrooms, bathrooms, squarefeet, stories):
    return -261898.85 + (379.62 * squarefeet) + (189063.88 * bedrooms) + (1206939.36 * bathrooms) + (531871.63 * stories)    


@app.route('/', methods=['GET', 'POST'])
def index():
    plot_url = None
    confidence_interval = None
    original_home_price = None
    modified_home_price = None
    roi_value = None
    error_message = None

    if request.method == 'POST':

        required_fields = ["area", "bedrooms_existing", "bathrooms_existing",
                   "bedrooms_addition", "bathrooms_addition", "kitchen",
                   "living_room", "modified_sqft", "additional_sqft", "second_story",
                   "high_end", "stories", "mainroad", "guestroom", "basement",
                   "hot_water_heating", "airconditioning", "parking", "prefarea",
                   "furnishing_status", "bedrooms_addition", "bathrooms_addition",
                   "kitchen", "living_room", "detached", "modified_sqft",
                   "additional_sqft", "second_story", "high_end"]


        if not all(request.form[field] for field in required_fields):
            error_message = "All fields must be filled out."
            print("Error Message:", error_message)  
        else:

            area = float(request.form["area"])
            bedrooms_existing = int(request.form["bedrooms_existing"])
            bathrooms_existing = int(request.form["bathrooms_existing"])
            stories_existing = int(request.form["stories"])
            mainroad_existing = int(request.form["mainroad"])
            guestroom_existing = int(request.form["guestroom"])
            basement_existing = int(request.form["basement"])
            hot_water_existing = int(request.form["hot_water_heating"])
            aircon_existing = int(request.form["airconditioning"])
            parking_existing = int(request.form["parking"])
            prefer_existing = int(request.form["prefarea"])
            furnished_existing = int(request.form["furnishing_status"])
    

            # original_home_price = predict_home_price(bedrooms_existing, bathrooms_existing, area)
            original_home_price = predict_home_price(bedrooms_existing, bathrooms_existing, area,stories_existing)

            bedrooms_addition = int(request.form["bedrooms_addition"])
            bathrooms_addition = int(request.form["bathrooms_addition"])
            kitchen = 1 if request.form["kitchen"] == 'y' else 0
            living_room = 1 if request.form["living_room"] == 'y' else 0
            detached = int(request.form["detached"])
            modified_sqft = float(request.form["modified_sqft"])
            additional_sqft = float(request.form["additional_sqft"])
            second_story = 1 if request.form["second_story"] == 'y' else 0
            high_end = float(request.form["high_end"])
    

            bedrooms_new = bedrooms_existing + bedrooms_addition
            bathrooms_new = bathrooms_existing + bathrooms_addition
            sqft_new = area + additional_sqft
    

            # modified_home_price = predict_home_price(bedrooms_new, bathrooms_new, sqft_new)
            modified_home_price = predict_home_price(bedrooms_new, bathrooms_new, sqft_new, stories_existing)
            tot_sqft = modified_sqft + additional_sqft
            #user_data = [bedrooms_addition, bathrooms_addition, kitchen, living_room, detached, modified_sqft, additional_sqft, second_story, tot_sqft]
            #samples = predict_cost_distribution(user_data, clf_mean, clf_sd, high_end)
            user_data = [
                bedrooms_addition,
                bathrooms_addition,
                kitchen,
                living_room,
                detached,
                modified_sqft,
                additional_sqft,
                second_story
            ]

            expected_cost,samples = cost_distribution_estimate_non_mp_version(user_data,high_end)

            expected_cost = np.mean(samples)
            

            increase_in_home_value = modified_home_price - original_home_price
            roi_value = (increase_in_home_value / expected_cost) - 1
    

            img = BytesIO()
            sns.kdeplot(samples, shade=True)
            plt.xlabel('Estimated Cost')
            plt.ylabel('Probability Density')
            plt.title('Estimated Cost Distribution')
            plt.ticklabel_format(style='plain', axis='y')
            plt.savefig(img, format="png")
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    

            lower_bound = np.percentile(samples, 2.5)
            upper_bound = np.percentile(samples, 97.5)
            confidence_interval = f"${lower_bound:.2f} - ${upper_bound:.2f}"

    return render_template('form.html', plot_url=plot_url, confidence_interval=confidence_interval, 
                           roi_value=roi_value, original_home_price=original_home_price, modified_home_price=modified_home_price, 
                           error_message=error_message)


if __name__ == '__main__':
    app.run(debug=True)


# ------------------------------------------------------------------------------
# Imports ----------------------------------------------------------------------
# ------------------------------------------------------------------------------


import os
import json
import requests
from datetime import datetime

from flask import Flask, request, jsonify, redirect, url_for, render_template, send_file, send_from_directory, render_template
from rest_api import REST_API_PORT



# ------------------------------------------------------------------------------
# Constants --------------------------------------------------------------------
# ------------------------------------------------------------------------------


UI_PORT = 5000



# ------------------------------------------------------------------------------
# Functions --------------------------------------------------------------------
# ------------------------------------------------------------------------------


ui_app = Flask( __name__ + "_ui" )

@ui_app.route( "/" )
def mission_page():
    """A simple function that retreives the pipeline job request page HTML.

    :returns: The HTML for the pipeline job request page.
    """

    with open( "ui.html", "r" ) as html:
        return html.read()


@ui_app.route( "/submit", methods=["POST"] )
def submit():
    """A function called upon submission of a pipeline job request. This
       function parses the user request form, retrieving the user request data.
       This data is then organized into a dictionary to be sent in a REST
       POST request to the REST API.

       :returns: The HTML for a thank you page.
    """

    mission = ""
    output = ""
    program_list = []
    included_program_list = []
    image_list = []
    source_list = []
    form = request.form


    for key in form.keys():
        if( key == "mission" ):
            mission = form[key]
            continue
        elif( key == "output" ):
            output = form[key]
            continue
        elif( key == "sources" ):
            source_list = form[key]
            source_list = source_list.split(',')
            continue


        program = key.split("!")

        # The submit button is sometimes included in the data, which breaks
        # things. This gets rid of it.
        if( len(program) != 2 ):
            continue

        name = program[0]
        attribute = program[1]

        if( "img" in name ):
            if( form[key] == "on" ):
                image_name = name.split("~")[1]
                # TODO: This will be the archival image format
                image_list.append( image_name )

            continue

        if( attribute == "check" and form[key] == "on" ):
            program_list.append([name, []])
            included_program_list.append( name )
        elif( name in included_program_list ):
            program_list[-1][1].append( [attribute, form[key]] )

    filename = datetime.now().strftime( "%Y_%m_%d_%H_%M_%S" )
    recipe = {"mission":mission, "tasks":program_list, "output": output, "images": image_list, "sources": source_list, "filename": filename }
    recipe_string = json.dumps( recipe )
    recipe_json = json.loads( recipe_string )
    requests.post( "http://localhost:" + str(REST_API_PORT) + "/submit", headers={"content-type": "application/json"}, json=recipe_json )

    page_string = ""
    return render_template("thank_you.html", text=filename)

@ui_app.route( "/handle_data", methods=["POST"] )
def handle_data():
    print( request.form )
    print( request.form["test"] )
    return "test"


# Sends a simple test
@ui_app.route( "/test" )
def test():

    #os.system( "curl http://localhost:" + str(REST_API_PORT) + "/test -X POST -d \"data=\"" )
    requests.post( "http://localhost:" + str(REST_API_PORT) + "/test", headers={"content-type": "application/json"}, json={} )

    return "test"


# Sends a more complex test, which passes in pre-generated recipe data
# TODO: Make curling nicer
@ui_app.route( "/dagtest" )
def dag_test():

    with open( "REST_json.json", "r" ) as recipe_file:
        recipe_json = json.load( recipe_file )
        #os.system( "curl http://localhost:" + str(REST_API_PORT) + "/dagtest -X POST -d \"data=" + json.dumps(data).replace(" ", "").replace( "\"", "\\\"") + "\"" )
        requests.post( "http://localhost:" + str(REST_API_PORT) + "/dagtest", headers={"content-type": "application/json"}, json=recipe_json )

    return "dag test"

@ui_app.route( "/download", methods=["POST"] )
def download():
    data = request.get_json()
    filename = data['file'][0]
    exists = os.path.isfile('./dags/' + filename + '.zip')
    if exists:
        print(exists)
        return send_file('./dags/' + filename + '.zip',
            mimetype='application/zip',
            attachment_filename='test.zip',
            as_attachment=True)

# ------------------------------------------------------------------------------
# Main -------------------------------------------------------------------------
# ------------------------------------------------------------------------------


if( __name__ == "__main__" ):
    ui_app.run( port=UI_PORT, debug=True )

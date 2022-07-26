'''*******************************
importing flask and dependencies
'''
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import json
import os
import reviewAnalayzer

from flask_ngrok import run_with_ngrok

app = Flask(__name__)
# run_with_ngrok(app)


@app.route("/", methods=["GET"])
def get_example():
    """GET in server"""
    return render_template("home.htm")


@app.route('/upload_file', methods=['POST'])
def upload_static_file():
    print("Got request in static files")
    # print(request.files)
    extention_list = ['csv']
    f = request.files['filename']
    g = request.files['filename']
    l = str(request.files['filename']).split("'")
    uploadedfilename = str(request.files['filename']).split("'")[1]
    filename = uploadedfilename.split('.')
    # print(filename)
    file_extension = filename[1]
    # print(file_extension)
    if(file_extension not in extention_list):
        print('Invalid format')
        resp = {"success": False, "response": "Invalid File format!"}
        return jsonify(resp), 400
    # print('inputfile')
    # print(f)
    f.save('input/inputfile.'+file_extension)
    print("processing file...")
    # calling app reviewer
    analyzer_result = reviewAnalayzer.mis()
    # analyzer_result=200
    if(analyzer_result == 200):
        resp = {"success": True, "response": "You can download the output file by clicking the below button",
                "fileUrl": 'input/inputfile.csv'}
        return jsonify(resp), 200
    else:
        resp = {"success": False, "response": "Some error in the app Analyser", }
        return jsonify(resp), 400


@app.route("/login", methods=["GET"])
def loginredirect():
    """GET in server"""
    return render_template("login.htm")


@app.route("/authenticator", methods=["POST"])
def authenticate():
    """GET in server"""
    data = request.get_data()
    dict_str = json.loads(data.decode())
    print(dict_str)
    sessionids = {'mithun': '1m1i1t1h1u1n',
                  'megha': 'm1e1g1h1a1', 'anyone': 'a1n1y1o1n1e1'}
    try:
        print('checking for username password')
        if(dict_str['username'] == 'mithun' and dict_str['password'] == 'sekar'):
            resp = {"success": True, "response": "Login Successful",
                    'sessionID': sessionids['mithun']}
            return jsonify(resp), 200
        if(dict_str['username'] == 'megha' and dict_str['password'] == 'ramesh'):
            resp = {"success": True, "response": "Login Successful",
                    'sessionID': sessionids['megha']}
            return jsonify(resp), 200
        if(dict_str['username'] == 'anyone' and dict_str['password'] == 'canlogin'):
            resp = {"success": True, "response": "Login Successful",
                    'sessionID': sessionids['anyone']}
            return jsonify(resp), 200
        resp = {"success": False,
                "response": "Username / Password Incorrect", 'sessionID': ''}
        return jsonify(resp), 400
    except Exception as err:
        print(err)
        try:
            print('Checking for session ID')
            print(dict_str['sessionID'])
            print('========================')
            if(dict_str['sessionID'] == sessionids['mithun'] or dict_str['sessionID'] == sessionids['megha'] or dict_str['sessionID'] == sessionids['anyone']):
                # print('success')
                resp = {"success": True, "response": "Login Successful",
                        'sessionID': ''}
                return jsonify(resp), 200
            else:
                resp = {"success": False, "response": "Redirection to login page    ",
                        'sessionID': ''}
                return jsonify(resp), 400
        except Exception as err:
            print(err)
            pass
    resp = {"success": False, "response": "Not the required format of data",
            'sessionID': ''}
    return jsonify(resp), 200


@app.route("/output", methods=["GET"])
def oututDelivery():
    """ 
    Returns the output csv file 
    """
    csv_dir = "./output"
    csv_file = "outputFile.csv"
    csv_path = os.path.join(csv_dir, csv_file)

    # Also make sure the requested csv file does exist
    if not os.path.isfile(csv_path):
        return "ERROR: file %s was not found on the server" % csv_file
    # Send the file back to the client
    return send_file(csv_path, as_attachment=True, attachment_filename=csv_file)


if __name__ == "__main__":
    app.run(debug=True)

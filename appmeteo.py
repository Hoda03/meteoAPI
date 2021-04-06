from flask import Flask, jsonify, render_template, request
import json
import requests
import datetime

METEO_API_KEY = "7aa8de3c1238b42a2b0281664f7a4607"

METEO_API_URL = "http://api.openweathermap.org/data/2.5/forecast?APPID=" + METEO_API_KEY

app = Flask(__name__)


@app.route('/api/meteo/tempmax')
def meteo():
    city = request.args.get('city')
    new_meteo_api_url = "http://api.openweathermap.org/data/2.5/forecast?" + "&q=" + city + "&APPID=" + "7aa8de3c1238b42a2b0281664f7a4607"
    # new_meteo_api_url = METEO_API_URL + "&q=" + city

    response = requests.get(new_meteo_api_url)
    content = json.loads(response.content.decode('utf-8'))

    # print(content)

    if response.status_code != 200:
        return jsonify({
            'status': 'error',
            'message': 'La requête à l\'API météo n\'a pas fonctionné. Voici le message renvoyé par l\'API : {}'.format(
                content['message'])
        }), 500
    else:
        data = []

        old_date = content["list"][0]["dt_txt"]
        old_date_time_obj = datetime.datetime.strptime(old_date, '%Y-%m-%d %H:%M:%S')
        old_day = old_date_time_obj.day

        old_temp_max = float(content["list"][0]["main"]["temp_max"])

        for prev in content["list"]:

            new_date = prev['dt_txt']

            new_date_time_obj = datetime.datetime.strptime(new_date, '%Y-%m-%d %H:%M:%S')

            if old_date_time_obj.day == new_date_time_obj.day:
                new_temp_max = float(prev["main"]["temp_max"])
                if old_temp_max < new_temp_max:
                    old_temp_max = new_temp_max

            else:
                data.append([old_temp_max, str(old_date_time_obj.day) + "/" + str(old_date_time_obj.month) + "/" + str(
                    old_date_time_obj.year)])
                old_date_time_obj = new_date_time_obj
                old_temp_max = float(prev["main"]["temp_max"])

        data.append([old_temp_max, str(old_date_time_obj.day) + "/" + str(old_date_time_obj.month) + "/" + str(
            old_date_time_obj.year)])

        return jsonify({
            'status': 'ok',
            'data': data
        })


@app.route('/api/meteo/pollution')
def pollution():
  city = request.args.get('city')

  date = request.args.get('date')  # form (10-02-2021)

  date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')

  new_meteo_api_url = "http://api.openweathermap.org/data/2.5/forecast?" + "&q=" + city + "&APPID=" + "7aa8de3c1238b42a2b0281664f7a4607"

  response = requests.get(new_meteo_api_url)
  content = json.loads(response.content.decode('utf-8'))

  if response.status_code != 200:
    return jsonify({
      'status': 'error',
      'message': 'La requête à l\'API météo n\'a pas fonctionné. Voici le message renvoyé par l\'API : {}'.format(
        content['message'])
    }), 500
  else:
    data = []

    temp_max = -1000  # imposible temp

    for prev in content["list"]:

      new_date = prev['dt_txt']

      date_time_obj = datetime.datetime.strptime(new_date, '%Y-%m-%d %H:%M:%S')

      if date_time_obj.day == date_obj.day and date_time_obj.month == date_obj.month and date_time_obj.year == date_obj.year:
        new_temp_max = float(prev["main"]["temp_max"])
        if temp_max < new_temp_max:
          temp_max = new_temp_max
          maxdatetime = prev['dt_txt']
          maxprev = prev

    #data.append({"date": maxdatetime,"temp_max": temp_max})

    dt = int(prev["dt"])
    lon = content["city"]["coord"]["lon"]
    lat = content["city"]["coord"]["lat"]

    air_pollution_api_url = "http://api.openweathermap.org/data/2.5/air_pollution/history?lat=" + str(lat) + "&lon=" + str(lon) + "&start=" + str(dt) + "&end=" + str(dt + 3600) + "&appid=" + "7aa8de3c1238b42a2b0281664f7a4607"

    response1 = requests.get(air_pollution_api_url)
    content2 = json.loads(response1.content.decode('utf-8'))

    if response1.status_code != 200:
      return jsonify({
        'status': 'error',
        'message': 'La requête à l\'API météo n\'a pas fonctionné. Voici le message renvoyé par l\'API : {}'.format(
          content['message'])
      }), 500
    else:
      for prev in content2["list"]:
        Concentration_CO = prev['components']["co"]
        Concentration_NO = prev['components']["no"]
        Concentration_no2 = prev['components']["no2"]
        Concentration_O3 = prev['components']["o3"]

        data.append({"date": maxdatetime, "temp_max": temp_max,"CO": Concentration_CO,"NO":Concentration_NO ,"no2":Concentration_no2,"O3":Concentration_O3 })


    return jsonify({
      'status': 'ok',
      'data': data
    })


if __name__ == '__main__':
    app.run(debug=True)

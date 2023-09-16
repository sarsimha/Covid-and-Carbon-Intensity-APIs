from flask import abort
from flask import Flask, jsonify
from datetime import tzinfo, timedelta, datetime

import requests

app = Flask(__name__)

CARBON_INTENSITY_API_URL = "https://api.carbonintensity.org.uk/regional/intensity/"
COVID19_API_URL = "https://api.coronavirus.data.gov.uk/generic/metric_availability/"

commonRegionData = {
    "north scotland": {"region": "1", "both": False},
    "south scotland": {"region": "2", "both": False},
    "north west england": {"both": True, "region": "3", "area_type": "region", "areaCode": "E12000002"},
    "north east england": {"both": True, "region": "4", "area_type": "region", "areaCode": "E12000001"},
    "yorkshire": {"both": True, "region": "5", "area_type": "region", "areaCode": "E12000003"},
    "north wales": {"both": True, "region": "6", "both": False},
    "south wales": {"region": "7", "both": False},
    "west midlands": {"both": True, "region": "8", "area_type": "region", "areaCode": "E12000005"},
    "east midlands": {"both": True, "region": "9", "area_type": "region", "areaCode": "E12000004"},
    "east england": {"both": True, "region": "10", "area_type": "region", "areaCode": "E12000006"},
    "south west england": {"both": True, "region": "11", "area_type": "region", "areaCode": "E12000009"},
    "south england": {"region": "12", "both": False},
    "london": {"both": True, "region": "13", "area_type": "region", "areaCode": "E12000007"},
    "south east england": {"both": True, "region": "14", "area_type": "region", "areaCode": "E12000008"},
    "england": {"both": True, "region": "15", "area_type": "nation", "areaCode": "E92000001"},
    "scotland": {"both": True, "region": "16", "area_type": "nation", "areaCode": "S92000003"},
    "wales": {"both": True, "region": "17", "area_type": "nation", "areaCode": "W92000004"},
}
    
@app.route('/singleDate/<date>/<regionName>')
def getSingleDate(date: str, regionName: str):       
    try:
        regionLower = regionName.lower()
        if (regionLower in commonRegionData):
            if(commonRegionData[regionLower]["both"] == False):
                abort(404, "Region does not exist in Covid and Carbon Databases")
            reg = commonRegionData[regionLower]
            regionId = reg["region"]
            areatype = reg["area_type"]
            code = reg["areaCode"]
            formattedDate = date[0:10]
            carbonApiURL = CARBON_INTENSITY_API_URL + date + "/fw24h/regionid/" + regionId
            covidAPUIRL = COVID19_API_URL + areatype + "/" + code
            covidData = requests.get(covidAPUIRL).json()
            carbonData = requests.get(carbonApiURL).json()
            finalCovidData = [sub for sub in covidData if sub["last_update"] == formattedDate]
            data = {
                "carbonIntensity": carbonData,
                "CovidData": finalCovidData
            }
            return jsonify(data)
        else: 
            abort(404, "Region does not exist in Carbon Intensity database")
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/range/<fromDate>/<toDate>/<region>')
def getRangeDates(fromDate: str, toDate: str, region: str):
    try:
        regionLower = region.lower()
        if (regionLower in commonRegionData):
            if(commonRegionData[regionLower]["both"] == False):
               abort(404, "Region does not exist in Covid and Carbon Databases")
            reg = commonRegionData[regionLower]
            regionId = reg["region"]
            areatype = reg["area_type"]
            code = reg["areaCode"]
            formattedStart = datetime.strptime(fromDate[0:10], '%Y-%m-%d').date()
            formattedEnd = datetime.strptime(toDate[0:10], '%Y-%m-%d').date()
            carbonApiURL = CARBON_INTENSITY_API_URL + fromDate + "/" + toDate + "/regionid/" + regionId
            covidAPUIRL = COVID19_API_URL + areatype + "/" + code
            carbonData = requests.get(carbonApiURL).json()
            covidData = requests.get(covidAPUIRL).json()
            finalCovidData = [sub for sub in covidData if (datetime.strptime(sub["last_update"], '%Y-%m-%d').date() >= formattedStart) if (datetime.strptime(sub["last_update"], '%Y-%m-%d').date() <= formattedEnd)]
            data = {
                "carbonIntensity": carbonData,
                "CovidData": finalCovidData
            }
            return jsonify(data)
        else: 
            abort(404, "Region does not exist in Carbon Intensity Database")
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == '__main__':
    app.run(debug=True)

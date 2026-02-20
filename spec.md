I'd like to develop a simple web app that can be deployed using Docker that evaluates weather data and water conditions and compares them against Reading Rowing Club's water safety rules to determine if it is safe to row today. 
# Functional Specifications
On starting up, the app should do the following things:
1. Connect to the UK Environment Agency's flood monitoring API at http://environment.data.gov.uk/flood-monitoring/id/measures/2200TH-flow--Mean-15_min-m3_s and retrieve all "items" listed in the json output and cache the results.

2. read the data from the University of Reading's METFiDAS weather observations page at https://www.met.reading.ac.uk/weatherdata/Reading_AWS_weather_report.html and cache the values for "Air temperature: ºC", "10-metre maximum 3-sec wind gust: m/s", and the date and timestamp of the observation listed at the top of the page.

When the page is viewed, the app should do the following:
1. Check the age of the cached data from the UK Environment Agency's flood monitoring API and the cached data from the University of Reading's METFiDAS weather observations page. If the cached data are older than 15 minutes, clear the cached data and retrieve fresh copies.

2. Calculate the rowing conditions for "Fours, Quads, Eights" and "Singles, Doubles, Pairs" based on the rules specified in file called "rules.md"

# Burk Transmitter Reading Web App
A Flask web app that allows Master Control operator to sign and submit radio transmitter readings to a SQL database.

# Features
* Creates submission form based on prefigured channels to be monitored.
* Integration with Burk API automagically fills out out form with Meter and Status Data. 
* Automated messages generated when:
  - Meter above or below limits defined in configuration
  - Site could not connect to Burk unit
  - Channel value manually changed
* Separate form to log EAS tests.
* Generate PDF reports for individual sites by date range. 
  - Includes any automated messages specific to site or Operator shift notes.
  - Histogram of the Meter values over time.

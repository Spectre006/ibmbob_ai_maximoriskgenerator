# Project Requirements

I am trying to build an web application for submititng in IBM BoB Hackathon. This application is  AI enabled Risk Assessment Generator which evaluates the work order and prepare JHA (Job Hazard Analysis) Report.

Most of the time Maximo technicians are not able to prepare JHA report for the work order which can pose a security risk. This tool will help them to prepare JHA report for the work order.

Below will be the flow of application:

1. Risk Assessor will open the Web application.
2. He will have option to select Site from drop down and type WO# for which he wants to prepare JHA report.
3. He will click on Submit button.
4. Application will fetch the WO details from Maximo via Maximo REST API.
5. Maximo API will provide response in JSON format.
6. Application will parse the JSON response and extract the required information.
7. Application will look for Work Order Description, Asset Description, Location Description and Tasks (WOACTIVITY) which are part of the JSON.  
8. Application will use the extracted information to generate the JHA report using AI and display below.
9. There is a button to download the JHA report as PDF.
10. Use report_design.png file for the report design.
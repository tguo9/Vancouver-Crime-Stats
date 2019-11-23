# Proposal for Group 108

## Motivation and Purpose

## Description of the Data
The dataset that we choose to visualize is a public dataset that can be downloaded from the Vancouver Police Department's Open Data: https://geodash.vpd.ca/opendata/. It is a collection of types, locations, dates and times of crimes occurred in City of Vancouver for the past 16 years.  The earliest date in the dataset is January 1, 2003, and the latest date is October 31, 2019.  
  
This dataset is available to the public and no special permit or registration is required.  As it contains temporal-spatial information of crimes, it can be a great guidance to policy makers for laying out community development plans.  As an individual living in Vancouver like ourselves, it can also serve as a reference for selecting residence.

There are 622,221 crime records in this dataset, and each crime record contains: (`TYPE`, `YEAR`, `MONTH`, `DAY`, `HOUR`, `MINUTE`, `HUNDRED_BLOCK`, `NEIGHBOURHOOD`, `X`, `Y`) columns . (`TYPE`) specifies 11 types of crimes (‘Break and Enter Commercial', 'Break and Enter Residential/Other', 'Homicide', 'Mischief', 'Offence Against a Person', 'Other Theft', 'Theft from Vehicle', 'Theft of Bicycle', 'Theft of Vehicle', 'Vehicle Collision or Pedestrian Struck (with Fatality)', 'Vehicle Collision or Pedestrian Struck (with Injury)'), and (`YEAR`, `MONTH`, `DAY`, `HOUR` and `MINUTE`) columns specify the date and time when the reported crime occurred.  To indicate the location of the crimes, we have (`HUNDRED_BLOCK` and `NEIGHBORHOOD`).  (`X` and `Y`) provides the coordinates in UTM Zone 10 format and will need to be converted into longitude and latitude if we want to render a map with GeoJSON.


## Description of APP  
The APP is intended to show the historical crime data in a geo-temporal form.  To achieve this, it will display a choropleth of City of Vancouver for showing neighbourhoods and a line chart for showing the relationship between crime count and time.   This APP will be interactive and allows its users to specify the neighbourhood, crime type, and time scale to gain more understanding of how crimes are correlated to the neighbourhoods and time.
  
On the choropleth, the number of crimes in different neighbourhoods is colour-coded so that users can easily relate the count of a crime type to its relative location in Vancouver.  A dropdown list will be added for choosing the crime type.  There will also be a slider bar for changing the year range of the crime data, in case some users might be interested in a more recent crime data.  
  
In the line chart, we intend to show how the count of crimes in a neighbourhood varies with time.  So, there will be two dropdown lists accompanying the line chart: one for selecting the neighbourhood, and the other for selecting the time scale.  This way, the users can easily see the specified neighbourhood’s criminal trend in terms of the time of the day or month of the year.

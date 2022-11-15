import arcpy
import math
arcpy.env.overwriteOutput = True

# Set up paths for the NHL rosters and nations shapefiles
nhlRosterFC = "C:/PSUGIS/GEOG485/GEOG485Lesson3/nhlrosters.shp"
nhlCountriesFC = "C:/PSUGIS/GEOG485/GEOG485Lesson3/Countries_WGS84.shp"

# Create variables where the field you're selecting from is CNTRY_NAME and the country is Sweden. These fields can be
# changed by the user if need be.
country = "Sweden"
countryNameField = "CNTRY_NAME"

# Create variables for the position and three variables for the hockey player positions. These are given the name
# 1, 2, and 3 because the user should be able to edit these variables to select different positions if they wish.
playerPosNameField = "position"
playerPos1 = "RW"
playerPos2 = "LW"
playerPos3 = "C"

try:
    # four separate where clauses are required. One for selecting the country and three for the positions in each of the
    # three shapefiles that will be created.
    countryWhereClause = countryNameField + " = '" + country + "'"
    playerPos1WhereClause = playerPosNameField + " = '" + playerPos1 + "'"
    playerPos2WhereClause = playerPosNameField + " = '" + playerPos2 + "'"
    playerPos3WhereClause = playerPosNameField + " = '" + playerPos3 + "'"

    # using SelectLayerByAttribute to select the country of choice (in this case Sweden) from the countries shapefile.
    # countryLayer uses CopyFeatures on selectCountryLayer to copy the new shapefile to the specified path.
    selectionCountryLayer = arcpy.SelectLayerByAttribute_management(nhlCountriesFC, 'NEW_SELECTION', countryWhereClause)
    countryLayer = arcpy.CopyFeatures_management(selectionCountryLayer, "C:/PSUGIS/GEOG485/GEOG485Lesson3/countryLayer")

    # playersLayer is the variable stored for selecting the players in the specified country. nationalityPlayersLayer
    # copies this into a new shapefile.
    playersLayer = arcpy.SelectLayerByLocation_management(nhlRosterFC, 'WITHIN', countryLayer)
    nationalityPlayersLayer = arcpy.CopyFeatures_management(playersLayer,
                                                            "C:/PSUGIS/GEOG485/GEOG485Lesson3/nationalityPlayersLayer")

    # positionsLayer1, 2, and 3 select players at the specified positions from the specified country.
    positionsLayer1 = arcpy.SelectLayerByAttribute_management(nationalityPlayersLayer, 'NEW_SELECTION',
                                                              playerPos1WhereClause)

    positionsLayer2 = arcpy.SelectLayerByAttribute_management(nationalityPlayersLayer, 'NEW_SELECTION',
                                                              playerPos2WhereClause)

    positionsLayer3 = arcpy.SelectLayerByAttribute_management(nationalityPlayersLayer, 'NEW_SELECTION',
                                                              playerPos3WhereClause)

    # selectedPositionsLayer1, 2, and 3 copies these features into new shapefiles.
    selectedPositionsLayer1 = arcpy.CopyFeatures_management(positionsLayer1,
                                                            "C:/PSUGIS/GEOG485/GEOG485Lesson3/selectedPositionsLayer1")
    selectedPositionsLayer2 = arcpy.CopyFeatures_management(positionsLayer2,
                                                            "C:/PSUGIS/GEOG485/GEOG485Lesson3/selectedPositionsLayer2")
    selectedPositionsLayer3 = arcpy.CopyFeatures_management(positionsLayer3,
                                                            "C:/PSUGIS/GEOG485/GEOG485Lesson3/selectedPositionsLayer3")

    # Creating a list of the shapefiles we will manipulate.
    fcList = [selectedPositionsLayer1, selectedPositionsLayer2, selectedPositionsLayer3]

    # For loop for the fcList we just created
    for fcName in fcList:
        # Add the required fields before entering the UpdateCursor.
        arcpy.AddField_management(fcName, "height_cm", "TEXT")
        arcpy.AddField_management(fcName, "weight_kg", "LONG")
        # Creating the UpdateCursor for each shapefile in the list and the field to be manipulated.
        with arcpy.da.UpdateCursor(fcName, ["height", "height_cm", "weight", "weight_kg"]) as cursor:
            # for the rows[0-3] corresponding to the fields in each shapefile...
            for row in cursor:
                heightImp = row[0]              # heightImp is row[0] in the cursor (heightImpField)
                feet = int(heightImp[0])        # Feet is the 0 index of the heightImp string.
                inString = heightImp[2:]   # Inches begin at the 2nd index to the end of the string.
                inches = int(inString.replace('"', ""))  # We can't have the '"' at the 4th index so remove it.
                feet_inches = feet*12 + inches   # Now that everything is int, calculate feet and add the inches.
                centimeters = feet_inches*2.54   # calculate cm
                row[1] = math.trunc(centimeters)    # Centimeters is the heightMetricField (row[1] in the cursor)
                weightImp = row[2]              # weightImp is row[2] (weightImpField) in the cursor.
                weightMet = int(weightImp*0.453592)     # Calculate the metric weight (kg)
                row[3] = weightMet              # Assign the metric weight to the weightMetricField, row[3] in cursor
                cursor.updateRow(row)           # update the rows

except arcpy.ExecuteError:
    print(arcpy.GetMessages("Something else went wrong. Oh No!"))

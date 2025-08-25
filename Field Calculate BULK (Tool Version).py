import arcpy
import os
import datetime

startTime = datetime.datetime.now().replace(microsecond=0)
print("Operation started on {}".format(startTime))

arcpy.env.addOutputsToMap = False

# When copy and pasting a file path, be sure the 'r' is at the begining, as shown below:
featureClass = arcpy.GetParameterAsText(0)
# Be sure to use the Field's Name not the Alias
fieldToUpdate = [arcpy.GetParameterAsText(1)]
fieldUpdateValue = arcpy.GetParameterAsText(2)
if fieldUpdateValue == "None" or fieldUpdateValue == "Null":
    fieldUpdateValue = None

fcDesc = arcpy.Describe(featureClass)
workspace = os.path.dirname(fcDesc.catalogPath)
wsDesc = arcpy.Describe(workspace)

if hasattr(wsDesc, "datasetType") and wsDesc.datasetType == 'FeatureDataset':
    workspace = os.path.dirname(workspace)
    domains = arcpy.da.ListDomains(workspace)
else:
    domains = arcpy.da.ListDomains(workspace)

for fieldName in fieldToUpdate:
    field = next(f for f in fcDesc.fields if f.name == fieldName)
    if field.domain:
        domain = next(d for d in domains if d.name == field.domain)
        if domain.domainType == 'CodedValue':
            # print(f"Field '{fieldName}' has a coded value domain.")
            if fieldUpdateValue in domain.codedValues.values():
                print(f"The value '{fieldUpdateValue}' is valid for field '{fieldName}'.")
            else:
                print(f"The value '{fieldUpdateValue}' is not valid for field '{fieldName}'.  Please calculate this"
                      f"field separately.")
                raise ValueError(f"The value '{fieldUpdateValue}' is not valid for field '{fieldName}'.  Please check"
                                 f" spelling otherwise calculate this field separately.")

batchUpdate = 10000
total = 0
done = False

def fieldUpdater():
    fieldDict = {}


while not done:
    count = 0
    with arcpy.da.Editor(workspace, multiuser_mode=fcDesc.isVersioned):
        with arcpy.da.UpdateCursor(featureClass, fieldToUpdate) as Cursor:
            for row in Cursor:
                updated = False
                if row[0] != fieldUpdateValue:
                    row[0] = fieldUpdateValue
                    updated = True
                    count += 1
                    total += 1
                # Use this if updating a SECOND field, notice row[1]
                # if row[1] is None:
                #     row[1] = fieldUpdateValue
                #     updated = True
                #     count += 1
                #     total += 1
                # Use this if updating a THIRD field, notice row[2].
                # if row[2] is None:
                #     row[2] = fieldUpdateValue
                #     updated = True
                #     count += 1
                #     total += 1
                # Copy the "if row" block above if needed for a row[3], row[4], etc....
                if updated:
                    Cursor.updateRow(row)
                if count >= batchUpdate:
                    print(f'done {count}')
                    break
        if count < batchUpdate:
            done = True
        print(f"Performed {total} updates so far.")

del fcDesc, wsDesc, workspace

arcpy.management.ApplySymbologyFromLayer(featureClass, featureClass, update_symbology="MAINTAIN")

endTime = datetime.datetime.now().replace(microsecond=0)
dur = endTime - startTime
dur = str(dur)
print('Duration: {}'.format(dur))

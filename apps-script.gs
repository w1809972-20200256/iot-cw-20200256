SHEET_NAME = "pico";
COUNTER_CELL = "E2";

function doGet(e) {
  var spreadSheet = SpreadsheetApp.getActiveSpreadsheet();
  var SHEET = spreadSheet.getSheetByName(SHEET_NAME);

  if (!SHEET) {
    return ContentService.createTextOutput("Error: Sheet not found");
  }

  // If running manually, provide mock parameters
  if (!e || !e.parameter) {
    e = {
      parameter: {
        time: "Sample Time",
        temp: "Sample Temperature",
        pressure: "Sample Pressure"
      }
    };
  }

  // Get current reading count from E2 (default to 0 if empty)
  var readingCount = SHEET.getRange(COUNTER_CELL).getValue();
  if (!readingCount || readingCount < 0) {
    readingCount = 0;
  }

  // Determine the next available row (first empty row after the header)
  var nextRow = readingCount + 2; // Starts from B2 (Row 2)

  // Assign parameters safely
  var timeValue = e.parameter.time || "No Time Data";
  var temperatureValue = e.parameter.temp || "No Temp Data";
  var pressureValue = e.parameter.pressure || "No Pressure Data";

  // Log data
  SHEET.getRange("B" + nextRow).setValue(timeValue);
  SHEET.getRange("C" + nextRow).setValue(temperatureValue);
  SHEET.getRange("D" + nextRow).setValue(pressureValue);

  // Increment and update the counter
  readingCount++;
  SHEET.getRange(COUNTER_CELL).setValue(readingCount);

  return ContentService.createTextOutput("Data logged successfully. Total readings: " + readingCount);
}

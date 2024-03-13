import openpyxl as xl
from openpyxl.drawing.spreadsheet_drawing import AnchorMarker, TwoCellAnchor
import pandas as pd

def createExcel(wbName, headers):
    wb = xl.Workbook()
    page = wb.active
    page.title = 'Simulation results'
    page.append(headers)
    page.freeze_panes = page['a2']
    wb.save(wbName)

def writeExcel(wbName, parameters, barPlt, timePlt):
    wb = xl.load_workbook(wbName)
    page = wb.active
    page.append(parameters)
    numrows = page.max_row
    page.column_dimensions['I'].width = 70
    page.column_dimensions['J'].width = 80
    page.row_dimensions[numrows].height= 240
    imgBar = xl.drawing.image.Image(barPlt)
    imgBar.anchor = TwoCellAnchor(editAs='twoCell', _from= AnchorMarker(col=8, row=str(numrows-1)), to=AnchorMarker(col=9, row=str(numrows)))
    page.add_image(imgBar)
    imgTime = xl.drawing.image.Image(timePlt)
    imgTime.anchor = TwoCellAnchor(editAs='twoCell', _from= AnchorMarker(col=9, row=str(numrows-1)), to=AnchorMarker(col=10, row=str(numrows)))
    page.add_image(imgTime)
    wb.save(wbName)
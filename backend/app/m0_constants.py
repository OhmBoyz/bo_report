# backend/app/m0_constants.py

# Chemins des fichiers
#REDCON_FILE_LOCATION = r"\\SOMEWHERE\\Dorval\\commun\\Documents Production\\BO REPORT\\REDCON FILE"
REDCON_FILE_LOCATION = r"C:/Users/Matthew/Desktop/BO_REPORT/REDCON"
#REDCON_WB_NAME = "REDCON PARTS.xlsx"
REDCON_WB_NAME = "RP_TEST.xlsx"
REDCON_FILENAME = REDCON_WB_NAME  # nom de fichier REDCON
OLD_REDCON_FILE_LOCATION = r"\\SOMEWHERE\\Dorval\\commun\\Documents Production\\BO REPORT\\OLD REDCON FILE"

#BACKLOG_FILE_LOCATION = r"\\SOMEWHERE\\Dorval\\commun\\Documents Production\\BO REPORT\\Backlog"
BACKLOG_FILE_LOCATION = r"C:/Users/Matthew/Desktop/BO_REPORT/REDCON"
#BACKLOG_WB_NAME = "BACKLOG.xlsx"  # à adapter
BACKLOG_WB_NAME = "BL_TEST.xlsx"
BACKLOG_FILENAME = BACKLOG_WB_NAME  # nom de fichier Backlog

# Noms des feuilles
WS_MAIN_NAME = "MAIN"
WS_TEMPLATE_NAME = "TEMPLATE"
WS_FLAG_NAME = "FLAG"
WS_PRINTLOG_NAME = "PRINTLOG"
WS_RAPPORTLOG_NAME = "RAPPORTLOG"

# Colonnes de la table MAIN
MAIN_COL_GO_ITEM = 1
MAIN_C_COL_GO_ITEM = "A"
MAIN_COL_ORACLE = 2
MAIN_C_COL_ORACLE = "B"
MAIN_COL_PART = 3
MAIN_C_COL_PART = "C"
MAIN_COL_QTY = 4
MAIN_C_COL_QTY = "D"
MAIN_COL_AMO = 5
MAIN_C_COL_AMO = "E"
MAIN_COL_SURPLUS = 6
MAIN_C_COL_SURPLUS = "F"
MAIN_COL_KB = 7
MAIN_C_COL_KB = "G"
MAIN_COL_FLOW_STATUS = 8
MAIN_C_COL_FLOW_STATUS = "H"
MAIN_COL_REDCON = 9
MAIN_C_COL_REDCON = "I"
MAIN_COL_PICK_STAT = 10
MAIN_C_COL_PICK_STAT = "J"
MAIN_COL_DISCRETE = 11
MAIN_C_COL_DISCRETE = "K"
MAIN_COL_QTY_REMAINING = 12
MAIN_C_COL_QTY_REMAINING = "L"
MAIN_COL_SHIPPING = 13
MAIN_C_COL_SHIPPING = "M"

# Constantes temporaires (templates)
TEMP_GO_LOCATION = "B2"
TEMP_CUSTOMER_LOCATION = "B3"
TEMP_ORACLE_LOCATION = "H2"
TEMP_JOB_NAME_LOCATION = "H3"
TEMP_COL_ORACLE_STATUS = 1
TEMP_C_COL_ORACLE_STATUS = "A"
TEMP_COL_ITEM = 2
TEMP_C_COL_ITEM = "B"
TEMP_COL_DISCRETE = 3
TEMP_C_COL_DISCRETE = "C"
TEMP_COL_PART = 4
TEMP_C_COL_PART = "D"
TEMP_COL_QTY = 5
TEMP_C_COL_QTY = "E"
TEMP_COL_AMO = 7
TEMP_C_COL_AMO = "G"
TEMP_COL_KB = 9
TEMP_C_COL_KB = "I"
TEMP_COL_SURPLUS = 11
TEMP_C_COL_SURPLUS = "K"
TEMP_COL_DATE = 12
TEMP_C_COL_DATE = "L"
TEMP_COL_SHIPPING = 13
TEMP_C_COL_SHIPPING = "M"

# Variables globales (initialisées via init_ws/init_redcon/init_bl)
glob_redcon_wb_name: str
glob_bl_wb_name: str

# (Optionnel) Déclarations des workbooks/worksheets
ws_main = None
ws_template = None
ws_flag = None
ws_print = None
ws_rap = None
wb_redcon = None
ws_redcon = None
wb_bl = None
ws_bl = None
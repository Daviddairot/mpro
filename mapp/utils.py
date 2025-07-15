from rest_framework_simplejwt.tokens import RefreshToken
 

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    
    
import openpyxl

def parse_excel(uploaded_file):
    workbook = openpyxl.load_workbook(uploaded_file)
    sheet = workbook.active
    rows = []

    for row in sheet.iter_rows(min_row=2, values_only=True):  # skip header
        rows.append(row)

    return rows

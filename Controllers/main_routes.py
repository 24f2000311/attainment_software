from flask import Blueprint, render_template, request
import os
from services.state import state, UPLOAD_FOLDER
from services.read_excels import read_excel_file
from services.validator import validate_config_sheets, validate_marks_basic
from services.normalizer import normalize_marks
from services.validator import validate_config_sheets, validate_marks_basic, validate_co_weights
from services.cleaning_normalized_data import clean_row

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/upload', methods=['POST'])
def upload():
    try:
        
        
        state.cqi_actions = []
        
        config_file = request.files['config']
        marks_file =  request.files['marks']
        
        config_path = os.path.join(UPLOAD_FOLDER, 'config.xlsx')
        marks_path = os.path.join(UPLOAD_FOLDER, 'marks.xlsx') 
        
        config_file.save(config_path)
        marks_file.save(marks_path)
        
        state.config_sheets = read_excel_file(config_path)
        marks_sheets = read_excel_file(marks_path)
        
        validate_config_sheets(state.config_sheets)
        validate_marks_basic(marks_sheets)
        
        # New Strict Validation for CO-wise weights
        if "CO_Weightage" in state.config_sheets:
             validate_co_weights(state.config_sheets["CO_Weightage"])
        else:
             raise ValueError("Missing 'CO_Weightage' sheet in config file.")
        
        question_map = state.config_sheets["Question_CO_Map"]
        co_weights_df = state.config_sheets["CO_Weightage"]
        
        # Create dictionary: (Assessment, CO_ID) -> Weight
        co_weights = dict(zip(
            zip(co_weights_df["Assessment"], co_weights_df["CO_ID"]),
            co_weights_df["Weight"]
        ))
        
        # Pass co_weights instead of assessment weights
        normalized_data = normalize_marks(marks_sheets, question_map, co_weights)
        state.cleaned_normalized_data = [clean_row(r) for r in normalized_data]

        
        return render_template('validate.html', messages=[ "Files uploaded successfully",
                    "Validation completed",
                    f"Normalized rows created: {len(state.cleaned_normalized_data)}"
                ])

    except ValueError as e:
        return render_template('error.html', error_message=str(e))

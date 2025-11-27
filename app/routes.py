import io
import json
import pandas as pd
from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for,make_response
from flask import jsonify
from .helper.video_processor import process_dataframe,process_json_data
from app.modals import PortfolioManager, VideoEmbed, ImageEmbed, SoundEmbed
import uuid
import datetime
import json
from .helper.handle_portfolio_item import handle_portfolio_item
from .helper.add_or_update_multicreator import add_or_update_multicreator
from .helper.generate_email import generate_email
from .helper.addMyCollection import addMyCollection
from .helper.addMyCollectionData import addMyCollectionData
from .helper.ImageConvert import ImageConvert
from .modals.multicreator import Multicreator
import pprint
main_bp = Blueprint(
    'main',
    __name__,
    template_folder='templates'  # <-- add this
)

@main_bp.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        if not uploaded_file:
            flash("No file selected")
            return redirect(request.url)

        # Read file to dataframe
        try:
            if uploaded_file.filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.filename.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                flash("Unsupported file type")
                return redirect(request.url)
        except Exception as e:
            flash(f"Error reading file: {e}")
            return redirect(request.url)

        if 'videos' not in df.columns:
            flash("No 'videos' column found in the file.")
            return redirect(request.url)

        df_processed = process_dataframe(df, max_rows=10)
        # Trim the DataFrame to max_rows
        df_trimmed = df_processed.head(10)
        output = io.BytesIO()
        df_trimmed.to_excel(output, index=False)
        output.seek(0)
        json_data = df.to_dict(orient='records')
        # return jsonify(json_data)
        response = make_response(send_file(
            output,
            as_attachment=True,
            download_name=f"{uploaded_file.filename.rsplit('.',1)[0]}_processed.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ))
        response.set_cookie('fileDownload', 'true', max_age=60, path='/')
        return response

    return render_template('upload.html')


@main_bp.route('/refine-data', methods=['POST'])
def process_json():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        if isinstance(data, dict):
            data = [data]

        processed_list = process_json_data(data)
        item = processed_list[0]

        # --- Process all credits ---
        credits_response = []
        multi_creator_ids = []

        for credit in item.get("credits", []):
            creatorName = credit.get("creatorName", "")
            email = generate_email(creatorName)  
            if not email:
                continue  

            firstname = credit.get("firstName", "") or creatorName
            lastname = credit.get("lastName", "")
            role = credit.get("role", "")
            normalized_role = role.strip().lower().replace(" ", "-")

           
            multicreator_entry, creator_entry, _, action = add_or_update_multicreator({
                "email": email,
                "firstname": firstname,
                "lastname": lastname,
                "profile_type": normalized_role,
                "Market_Category":item['Market_Category']
            })
            if multicreator_entry: 
                multi_creator_ids.append(str(multicreator_entry.id))

            credits_response.append({
                "creatorName": creatorName,
                "email": email,
                "profile_type": normalized_role,
                "status_multicreator": action.get("multicreator"),
                "id_multicreator": str(multicreator_entry.id) if multicreator_entry else None,
                "status_creator": action.get("creator"),
                "id_creator": str(creator_entry.id) if creator_entry else None
            })

        item["multiCreatorIds"] = multi_creator_ids
        item["multiCreatorIdsProfileType"] = credits_response

        portfolio_entry = handle_portfolio_item(item,normalized_role)
        portfolio_entry_id= str(portfolio_entry.id)
        
        #here handle collection as added new if not exstiing
        resultMyCollection=addMyCollection(item)
        collections_ids = resultMyCollection['collections_ids']
        
        
        # pprint.pprint("testing-123 68dcb88935cd74a53f964374 " \
        # "{collectionId:ObjectId('68dcb88935cd74a53f964374'),projectId:ObjectId('68de507c52fef3e403769348')}"
        
        # )
        # pprint.pprint(collections_ids)
        # pprint.pprint(resultMyCollection)
        #here handle for mycollectiondatas
        addMyCollectionData(collections_ids,portfolio_entry_id)
        return jsonify({
            "status": "success",
            "item": item,
            "credits": credits_response
        }), 200

    except Exception as e:
        return jsonify({"error": f"Processing failed: {e}"}), 500

@main_bp.route('/webp/<int:pageNumber>', methods=['POST'])
def process_image(pageNumber):
    try:
        return ImageConvert(pageNumber)
    except Exception as e:
        return jsonify({"error": f"Processing failed: {e}"}), 500


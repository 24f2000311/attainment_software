from flask import Blueprint, render_template, request, flash, redirect, url_for
from services.license_service import LicenseService

activation_bp = Blueprint('activation_bp', __name__)

@activation_bp.route('/activate', methods=['GET', 'POST'])
def activate():
    if request.method == 'POST':
        key = request.form.get('product_key', '')
        if LicenseService.activate(key):
            flash("Activation successful! Welcome.", "success")
            return redirect(url_for('main.index'))
        else:
            flash("Invalid or corrupted product key.", "error")
            
    # If already activated, redirect to home
    if LicenseService.is_activated():
         return redirect(url_for('main.index'))
         
    return render_template('activation.html')

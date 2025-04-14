from flask import Blueprint, render_template, send_from_directory

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('templates/css', filename)

@main_bp.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('templates/js', filename)

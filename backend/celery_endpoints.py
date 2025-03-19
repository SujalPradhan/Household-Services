from tasks import create_resource_csv, celery_app
from celery.result import AsyncResult
from flask import Flask, jsonify, send_file
from flask_restful import Resource


# @app.get('/downloadcsv')
# def download_csv():
class DownloadCSV(Resource):
    def get(self):
        task = create_resource_csv.delay()
        return {"task_id": task.id}

# @app.get('/getcsv/<task_id>')
# def get_csv(task_id):
class GetCSV(Resource):
    def get(self, task_id):
        res = AsyncResult(task_id, app=celery_app)
        if res.ready():
            filename = res.result
            return send_file(filename, as_attachment=True)
        
        else:
            return jsonify({"status": "Task pending"}), 400
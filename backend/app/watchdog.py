import logging
import os
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from app.celery_tasks import process_markdown
from app.core.config import settings

logger = logging.getLogger(__name__)



class PDFHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.pdf'):
            pdf_path = event.src_path
            filename = os.path.basename(pdf_path)
            metadata_path = os.path.dirname(pdf_path)
            metafname, _ = os.path.splitext(filename)
            metadata_path = os.path.join(metadata_path, metafname + '.json')
            print(f"Processing PDF: {pdf_path}")
            print(f"Processing metadata: {metadata_path}")
            #process_pdf.delay(pdf_path, metadata_path)
            #start_pdf_processing.delay(pdf_path, metadata_path)
            process_markdown.delay("/Users/panta/fastapi-jlabgpt/backend/filesupload/mds/a.md")

def start_watchdog():
    event_handler = PDFHandler()
    observer = Observer()
    observer.schedule(event_handler, path=settings.UPLOAD_DIR, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

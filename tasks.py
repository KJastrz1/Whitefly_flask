from app import celery, db, app
from app import Message
import logging

logger = logging.getLogger(__name__)

@celery.task
def process_message(content):
    print(f"Processing message: {content}")
    logger.info("Entering process_message task")
    with app.app_context():
        try:
            logger.info(f"Processing message: {content}")
            message = Message(content=content)
            db.session.add(message)
            db.session.commit()
            logger.info("Message added to database")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error processing message: {e}")
        finally:
            db.session.remove()
    logger.info("Exiting process_message task")

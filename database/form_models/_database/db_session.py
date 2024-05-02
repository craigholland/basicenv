import logging
from form_models._database import db


def cleanup_db_session():
    try:
        db.session.rollback()
        db.session.expire_all()
        db.session.remove()
    except Exception as e:
        logging.warning(e)

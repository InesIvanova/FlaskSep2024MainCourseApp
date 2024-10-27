from decouple import config
from flask import jsonify

from config import create_app
from db import db

environment = config("CONFIG_ENV")
app = create_app(environment)


@app.teardown_request
def commit_transaction_on_teardown(exception=None):
    """Commit the transaction if there's no exception."""
    if exception is None:
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return (
                jsonify(
                    {
                        "error": "An error occurred while saving data. Please try again later."
                    }
                ),
                500,
            )
    else:
        # Rollback after a flush if an error occurs to maintain session integrity:
        # - Flush may cause errors if it violates database constraints (e.g., unique, foreign key),
        #   putting the session in a failed state. Further DB operations will fail until rollback.
        # - SQLAlchemy treats the session as a single transaction. Without rollback, failed flushes
        #   leave the session in an invalid state, risking further errors on additional operations.
        # - Rollback clears any "dirty" data left by failed flushes, ensuring a clean session for
        #   the next steps and preventing data contamination in complex workflows.

        db.session.rollback()  # rollback in case of any exception
        return (
            jsonify(
                {
                    "error": "An unexpected error occurred. Please contact support if the issue persists."
                }
            ),
            500,
        )


@app.teardown_appcontext
def shutdown_session(response, exception=None):
    """
    Ensure a clean database session after each request by removing the current session.

    This method closes and removes the active session after each request:
    - Prevents session reuse across requests, ensuring no lingering data or connections persist.
    - Helps avoid unintended side effects from shared sessions between requests and reduces
      the risk of memory leaks from idle database connections.
    - Promotes stability by creating a fresh session for each request, supporting better isolation
      and reliability in database interactions.

    :param response:
    :param exception:
    :return:
    """
    db.session.remove()
    return response

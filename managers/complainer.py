from werkzeug.exceptions import Unauthorized, NotFound
from werkzeug.security import generate_password_hash, check_password_hash

from db import db
from managers.auth import AuthManager
from models import RoleType, UserModel, ComplaintModel, State, TransactionModel
from services.wise import WiseService

wise_service = WiseService()

class ComplainerManager:
    @staticmethod
    def login(data):
        user = db.session.execute(db.select(UserModel).filter_by(email=data["email"])).scalar()
        if user and check_password_hash(user.password, data["password"]):
            return AuthManager.encode_token(user)
        raise Unauthorized()

    @staticmethod
    def register(complainer_data):
        complainer_data["password"] = generate_password_hash(
            complainer_data["password"], method="pbkdf2:sha256"
        )
        complainer_data["role"] = RoleType.complainer.name
        user = UserModel(**complainer_data)
        db.session.add(user)
        db.session.flush()
        return AuthManager.encode_token(user)

    @staticmethod
    def get_claims(user):
        query = db.select(ComplaintModel)
        if user.role.complainer == RoleType.complainer:
            query = query.filter_by(complainer_id=user.id)
        return db.session.execute(query).scalars().all()

    @staticmethod
    def create(user, data):
        data["complainer_id"] = user.id
        c = ComplaintModel(**data)
        db.session.add(c)
        db.session.flush()
        ComplainerManager.issue_transaction(data["amount"], user.first_name, user.last_name, user.iban, c.id)

    @staticmethod
    def approve(complaint_id):
        complaint = db.session.execute(db.select(ComplaintModel).filter_by(id=complaint_id)).scalar()


        if not complaint:
            raise NotFound(f"Complaint with id {complaint_id} does not exist")
        transaction = db.session.execute(db.select(TransactionModel).filter_by(complaint_id=complaint.id)).scalar()
        wise_service.fund_transfer(transaction.transfer_id)
        complaint.status = State.approved
        db.session.add(complaint)
        db.session.flush()

    @staticmethod
    def reject(complaint_id):
        complaint = db.session.execute(db.select(ComplaintModel).filter_by(id=complaint_id)).scalar()
        if not complaint:
            raise NotFound(f"Complaint with id {complaint_id} does not exist")
        transaction = db.session.execute(db.select(TransactionModel).filter_by(complaint_id=complaint.id)).scalar()
        wise_service.cancel_transfer(transaction.transfer_id)
        complaint.status = State.rejected
        db.session.add(complaint)
        db.session.flush()

    @staticmethod
    def issue_transaction(amount, first_name, last_name, iban, complaint_id):
        quote = wise_service.create_quote(amount)
        recipient = wise_service.create_recipient(first_name, last_name, iban)
        transfer = wise_service.create_transfer(recipient["id"], quote["id"])
        t = TransactionModel(quote_id=quote["id"], transfer_id=transfer["id"], target_account_id=recipient["id"], amount=amount, complaint_id=complaint_id)
        db.session.add(t)
        db.session.flush()
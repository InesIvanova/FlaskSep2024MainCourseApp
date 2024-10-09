from resources.auth import RegisterComplainer, Login, Password
from resources.complaint import ComplaintListCreate, ComplaintApprove, ComplaintReject
from resources.user import User

routes = (
    (RegisterComplainer, "/register"),
    (Login, "/login"),
    (ComplaintListCreate, "/complainers/complaints"),
    (ComplaintApprove, "/approvers/complaints/<int:complaint_id>/approve"),
    (ComplaintReject, "/approvers/complaints/<int:complaint_id>/reject"),
    (User, "/admins/users"),
    (Password, "/users/change-password"),
)

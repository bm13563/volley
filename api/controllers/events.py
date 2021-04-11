from flask import Blueprint, current_app, request, g, jsonify
from flask_login import login_required
from ..models.events import Event, Metadata, Status, Setting, Description, Document, Parameters
from ..models.users import User
from ..utilities.utilities import str_to_date


blueprint = Blueprint('events', __name__, url_prefix="/events")

@blueprint.route("/add", methods=["POST"])
@login_required
def add():
    """
    Add an event to the Events collection.
    POST example for postman - https://www.getpostman.com/collections/2fbc6714da799092592b
    """
    args = request.get_json()

    # get status
    status = Status()

    # get metadata
    # owner is the user that is creating the event ie. the user that is currently logged in
    owner = User.objects.get(id=str(g.user.id))
    metadata = Metadata(
        category=args["category"],
        # embed the document of the user that created the collection as a reference
        owner=owner,
    )

    # get the setting
    setting = Setting(
        event_start=str_to_date(args["event_start"]), 
        event_end=str_to_date(args["event_end"]), 
        location=args["location"],
    )

    # get the description
    description = Description(
        name=args["name"],
        summary=args["summary"],
        social=args["social"],
    )

    # get the documents. the explanation for each document is passed as a list so we need to iterate through them
    documents = []
    for explanation in args["explanations"]:
        document = Document(
            explanation=explanation,
        )
        documents.append(document)

    # get the parameters
    parameters = Parameters(
        max_attendance=args["max_attendance"],
        documents=documents,
    )

    # pack embedded documents into the parent event document
    event = Event(
        metadata=metadata, 
        status=status, 
        setting=setting,
        description=description,
        parameters=parameters,
    )

    # validate, upload to database and return
    event.validate()
    event.save()

    # add the event to the owner's document
    owner.make_event_owner(event.id)
    owner.validate()
    owner.save()

    event_id = str(event.id)
    return {
        event_id: event.metadata.category
    }
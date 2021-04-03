from flask import Blueprint, current_app, request, g, jsonify
from ..models.events_model import Event, Metadata, Status, Setting, Description, Document, Parameters
from ..utilities.utilities import str_to_date

import pprint

blueprint = Blueprint('events', __name__, url_prefix="/events")

@blueprint.route("/add", methods=["POST"])
def add():
    """
    Add an event to the Events collection.
    """
    # parse mandatory arguments
    args = {}
    # we want to pass our arguments as json in the post, so have better control over types
    request_json = request.get_json()
    for argument in ["category", "event_start", "event_end", "x_location", "y_location", "name", "summary", "social", "max_attendance", "explanations"]:
        if argument in request_json.keys():
            args[argument] = request_json[argument]
        else:
            return jsonify({"error": f"please supply {argument} for the event"})

    # construct child documents
    status = Status()
    # get metadata
    metadata = Metadata(category=args["category"])
    # get the setting
    setting = Setting(
        event_start=str_to_date(args["event_start"]), 
        event_end=str_to_date(args["event_end"]), 
        location=[float(args["x_location"]), float(args["y_location"])],
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

    # pack our documents into the parent event document
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
    event_id = str(event.id)
    return {
        event_id: event.metadata.category
    }
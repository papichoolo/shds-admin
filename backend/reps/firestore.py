from google.cloud import firestore

def fs():
    # pin to your named database
    return firestore.Client(project="primeval-gizmo-474808-m7", database="shdsdb")



class ChrisJones:
    def __init__(self):
        # Do ES auth stuff
        print 'ChrisJones activated'

    def respond(self, query):
        # determine question type
        # then generate appropriate response

        # for now, just return the same stuff all the time
        return 'You said "' + query + '"'

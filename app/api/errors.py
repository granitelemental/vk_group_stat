class NotAuthorizedError(Exception):
    def __init__(self, *args, **kwargs):
        super(self, *args, **kwargs)
        self.code = 401

class NotFoundError(Exception):
    def __init__(self, *args, **kwargs):
        super(self, *args, **kwargs)
        self.code = 404

class CustomError(Exception):
    def __init__(self, *args, **kwargs):
        super(self, *args, **kwargs)
        self.code = 500

class ForbiddenError(Exception):
    def __init__(self, *args, **kwargs):
        super(self, *args, **kwargs)
        self.code = 403

class BadRequestError(Exception):
    def __init__(self, *args, **kwargs):
        super(self, *args, **kwargs)
        self.code = 400

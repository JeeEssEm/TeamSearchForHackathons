class Service:
    def __init__(self, session):
        annotations = self.__class__.__annotations__
        self.repository = annotations['repository'](session)

    @classmethod
    async def constructor(cls, factory):
        async with factory() as session:
            return cls(session)

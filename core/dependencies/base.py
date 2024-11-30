class BaseWithSessionObject:
    @classmethod
    async def constructor(cls, factory):
        async with factory() as session:
            return cls(session)

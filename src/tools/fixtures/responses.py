import factory

from storage.sqlalchemy.tables import Response


class ResponseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Response

    id = factory.Sequence(lambda n: n)
    user_id = factory.Sequence(lambda n: n)
    job_id = factory.Sequence(lambda n: n)
    message = factory.Faker("pystr")

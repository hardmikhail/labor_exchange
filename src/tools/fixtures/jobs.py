from datetime import datetime

import factory

from storage.sqlalchemy.tables import Job


class JobFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Job

    id = factory.Sequence(lambda n: n)
    user_id = factory.Sequence(lambda n: n)
    title = factory.Faker("sentence")
    description = factory.Faker("text")
    salary_from = factory.Faker("pydecimal", left_digits=7, right_digits=2, min_value=0)
    salary_to = factory.Faker("pydecimal", left_digits=7, right_digits=2, min_value=0)
    is_active = factory.Faker("pybool")
    created_at = factory.LazyFunction(datetime.now)

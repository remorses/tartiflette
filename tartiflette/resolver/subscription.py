from inspect import isasyncgenfunction
from typing import Callable

from tartiflette.schema.registry import SchemaRegistry
from tartiflette.types.exceptions.tartiflette import (
    MissingImplementation,
    NonAsyncGeneratorSubscription,
    UnknownFieldDefinition,
)


class Subscription:
    def __init__(self, name: str, schema_name: str = "default") -> None:
        self._name = name
        self._implementation = None
        self._schema_name = schema_name

    @property
    def name(self) -> str:
        return self._name

    def bake(self, schema: "GraphQLSchema") -> None:
        if not self._implementation:
            raise MissingImplementation(
                "No implementation given for subscription < %s >" % self._name
            )

        try:
            field = schema.get_field_by_name(self._name)
            field.subscribe = self._implementation
        except KeyError:
            raise UnknownFieldDefinition(
                "Unknown Field Definition %s" % self._name
            )

    def __call__(self, implementation: Callable) -> Callable:
        if not isasyncgenfunction(implementation):
            raise NonAsyncGeneratorSubscription(
                "The subscription `{}` given is not an awaitable "
                "generator.".format(repr(implementation))
            )

        SchemaRegistry.register_subscription(self._schema_name, self)
        self._implementation = implementation
        return implementation

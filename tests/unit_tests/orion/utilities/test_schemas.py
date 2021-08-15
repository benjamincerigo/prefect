import pytest
import pydantic
from prefect.orion.utilities.schemas import PrefectBaseModel, pydantic_subclass


class TestExtraForbidden:
    def test_extra_attributes_are_forbidden_during_unit_tests(self):
        class Model(PrefectBaseModel):
            x: int

        with pytest.raises(pydantic.ValidationError):
            Model(x=1, y=2)


class TestPydanticSubclass:
    class Parent(pydantic.BaseModel):
        class Config:
            extra = "forbid"

        x: int
        y: int = 2

    def test_subclass_is_a_subclass(self):
        Child = pydantic_subclass(self.Parent)
        assert issubclass(Child, self.Parent)

    def test_parent_is_unchanged(self):
        original_fields = self.Parent.__fields__.copy()
        Child = pydantic_subclass(self.Parent)
        assert self.Parent.__fields__ == original_fields

    def test_default_subclass_name(self):
        Child = pydantic_subclass(self.Parent)
        assert Child.__name__ == "Parent"

    def test_pydantic_does_not_issue_warning_when_creating_subclass(self):
        with pytest.warns(None) as record:
            pydantic_subclass(self.Parent)
        assert len(record) == 0

    def test_subclass_name(self):
        Child = pydantic_subclass(self.Parent, name="Child")
        assert Child.__name__ == "Child"

    def test_subclass_fields(self):
        Child = pydantic_subclass(self.Parent, name="Child")
        c = Child(x=1)
        assert c.x == 1
        assert c.y == 2

    def test_subclass_include_fields(self):
        Child = pydantic_subclass(self.Parent, name="Child", include_fields=["y"])
        c = Child(y=1)
        assert c.y == 1
        assert not hasattr(c, "x")

    def test_subclass_exclude_fields(self):
        Child = pydantic_subclass(self.Parent, name="Child", exclude_fields=["x"])
        c = Child(y=1)
        assert c.y == 1
        assert not hasattr(c, "x")

    def test_subclass_include_invalid_fields(self):
        with pytest.raises(ValueError, match="(fields not found on base class)"):
            pydantic_subclass(self.Parent, name="Child", include_fields=["z"])

    def test_subclass_exclude_invalid_fields(self):
        with pytest.raises(ValueError, match="(fields not found on base class)"):
            pydantic_subclass(self.Parent, name="Child", exclude_fields=["z"])

    def test_extend_subclass(self):
        class Child(pydantic_subclass(self.Parent, include_fields=["y"])):
            z: int

        c = Child(y=5, z=10)
        assert c.y == 5
        assert c.z == 10

    def test_extend_subclass_respects_config(self):
        class Child(pydantic_subclass(self.Parent, include_fields=["y"])):
            z: int

        with pytest.raises(
            pydantic.ValidationError, match="(extra fields not permitted)"
        ):
            Child(y=5, z=10, q=17)

    def test_validators_for_missing_fields_are_ok(self):
        class Parent2(pydantic.BaseModel):

            x: int
            y: int = 2

            @pydantic.validator("x")
            def x_greater_10(cls, v):
                if v <= 10:
                    raise ValueError()
                return v

        # child has a validator for a field that it doesn't include
        # and no error is raised during creation
        child = pydantic_subclass(Parent2, include_fields=["y"])
        with pytest.raises(ValueError):
            child.x_greater_10(5)


class TestClassmethodSubclass:
    class Parent(PrefectBaseModel):
        x: int
        y: int

    def test_classmethod_creates_subclass(self):
        Child = self.Parent.subclass("Child", include_fields=["x"])
        assert Child.__name__ == "Child"
        assert Child(x=1)
        assert not hasattr(Child(x=1), "y")


class TestNestedDict:
    @pytest.fixture()
    def nested(self):
        class Child(pydantic.BaseModel):
            z: int

        class Parent(PrefectBaseModel):
            x: int
            y: Child

        return Parent(x=1, y=Child(z=2))

    def test_full_dict(self, nested):
        assert nested.dict() == {"x": 1, "y": {"z": 2}}
        assert isinstance(nested.dict()["y"], dict)

    def test_simple_dict(self, nested):
        assert dict(nested) == {"x": 1, "y": nested.y}
        assert isinstance(dict(nested)["y"], pydantic.BaseModel)

    def test_shallow_true(self, nested):
        assert dict(nested) == nested.dict(shallow=True)
        assert isinstance(nested.dict(shallow=True)["y"], pydantic.BaseModel)

    def test_kwargs_respected(self, nested):
        deep = nested.dict(include={"y"})
        shallow = nested.dict(include={"y"}, shallow=True)
        assert isinstance(deep["y"], dict)
        assert isinstance(shallow["y"], pydantic.BaseModel)
        assert deep == shallow == {"y": {"z": 2}}

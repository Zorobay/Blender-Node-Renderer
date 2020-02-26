from bpy.props import FloatProperty, FloatVectorProperty, BoolProperty
from bpy.types import PropertyGroup


class FLOAT_SOCKET_PG_UserProperties(PropertyGroup):
    user_min: FloatProperty(
        name="User Min",
        description="The minimum value that this input parameter will take during render",
        default=0,
    )

    user_max: FloatProperty(
        name="User Max",
        description="The maximum value that this input parameter will take during render",
        default=1,
    )


class FLOAT_FACTOR_SOCKET_PG_UserProperties(PropertyGroup):
    user_min: FloatProperty(
        name="User Min",
        description="The minimum value that this input parameter will take during render",
        default=0,
        min=0,
        max=1,
    )

    user_max: FloatProperty(
        name="User Max",
        description="The maximum value that this input parameter will take during render",
        default=1,
        min=0,
        max=1,
    )


class FLOAT_VECTOR_SOCKET_PG_UserProperties(PropertyGroup):
    user_min: FloatVectorProperty(
        name="User Min",
        description="The minimum value that this input parameter will take during render",
        default=(0, 0, 0),
        subtype="XYZ"
    )

    user_max: FloatVectorProperty(
        name="User Max",
        description="The maximum value that this input parameter will take during render",
        default=(1, 1, 1),
        subtype="XYZ"
    )


class COLOR_SOCKET_PG_UserProperties(PropertyGroup):
    user_min: FloatVectorProperty(
        name="User Min",
        description="The minimum value that this input parameter will take during render",
        min=0,
        max=1,
        default=(0,0,0),
        subtype="XYZ",
        precision=3
    )

    user_max: FloatVectorProperty(
        name="User Max",
        description="The maximum value that this input parameter will take during render",
        min=0,
        max=1,
        default=(1,1,1),
        subtype="XYZ",
        precision=3
    )
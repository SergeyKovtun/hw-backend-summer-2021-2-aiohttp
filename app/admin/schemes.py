from marshmallow import Schema, fields


class AdminSchemaIn(Schema):
    email = fields.String(required=True)
    password = fields.String(required=True)


class AdminSchemaOut(Schema):
    id = fields.Integer()
    email = fields.Email()

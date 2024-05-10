from Application import EnumStore
from werkzeug.http import HTTP_STATUS_CODES as hsc

ErrorSchema = EnumStore.JSONSchema.Error

def check_error(code: int, msg: str, res: dict):
	assert res[ErrorSchema.CODE.value] == code
	assert res[ErrorSchema.NAME.value] == hsc[code]
	assert res[ErrorSchema.DESCRIPTION.value] == msg
SUCCESS = 0
PARSE_ERROR = 1
ERROR_MSGNAME = 2
WRONG_USERID_OR_PASSWORD = 102
USERID_EXISTED = 103
USERID_NOT_EXISTED = 104
ROLEID_NOT_EXISTED = 105
DATABASE_ERROR = 201
MAX_ROLE = 202
NEED_LOGIN = 301
MISSING_ARGUMENT = 401


ERROR_MSG = {
             SUCCESS : 'Success',
             PARSE_ERROR : 'Message parse error.',
             ERROR_MSGNAME : "Error msgname[%s]",
             WRONG_USERID_OR_PASSWORD : 'Wrong userid or password.',
             USERID_EXISTED : 'This userid has existed.',
             USERID_NOT_EXISTED : 'userid is not existed!',
             ROLEID_NOT_EXISTED : 'roleid is not existed!',
             DATABASE_ERROR : 'server database error.',
             MAX_ROLE : 'you have created 3 roles!',
             NEED_LOGIN : 'please login first.',
             MISSING_ARGUMENT : 'missing argument. needs[%s].',
}

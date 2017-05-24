DATABASE_SCHEMA = {
    'definitions' : {
        'mysql' : {
            'type' : 'object',
            'properties' : {
                'username' : {
                    'type' : ['string'],
                },
                'password' : {
                    'type' : ['string'],
                },
                'host' : {
                    'type' : ['string'],
                },
                'database_name' : {
                    'type' : ['string'],
                },
            },
            'required' : ['username', 'password', 'host', 'database_name'],
        },
        'sqlite' : {
            'type' : 'object',
            'properties' : {
                'database_file' : {
                    'type' : ['string', 'null'],
                },
            },
            'required' : ['database_file'],
        },
    },

    'type' : 'object',
    'properties' : {
        'mysql' : {
            '$ref' : '#/definitions/mysql',
        },
        'sqlite' : {
            '$ref' : '#/definitions/sqlite',
        },
    },
    'oneOf' : [
        {'required' : ['mysql']},
        {'required' : ['sqlite']},
    ],
}

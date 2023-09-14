
class ConfigValue:
    '''
    This class represents a config parameter assigned to a particular value
    It will also store the comment associated with this parameter
    '''
    def __init__(self, section, param, value, comment):
        '''
        section = the section the parameter appears in (string)
        param = the name of the parameter (string)
        value = the value of the parameter, can be a string or a parsed value (such as a float)
        comment = a list of the comment lines above this parameter, with the semicolon removed
        '''
        self.section = section
        self.param = param
        self.value = value
        self.comment = comment
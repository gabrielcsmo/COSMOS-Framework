from pydoc import locate

class Parameter():
    def __init__(self, **kwargs):
        """Form a Task Parameter

        Mandatory params:
        name    : string that is used when param is used.
                  Can be --name=value or just <value>
        value   : must be a string, int or float
        type    : must be "str", "int", "float"
                  this must be valid type for <value> param

        Optional params:
        dir     : if specified, can be used if <type> is int
                  or float and it decides the <value> for this
                  Parameter() in the next step.
                  Must be -1 or +1 and value = value + (dir * step)
        step    : if specified, can be used if <type> is int
                  or float and it decides the <value> for this
                  Parameter() in the next step.
                  Must have the same type as <type> and
                  value = value + (dir * step)
        """

        """Mandatory args"""
        if 'name' not in kwargs:
            raise KeyError("Cannot init parameter without name")
        self.name = kwargs['name']

        if 'type' not in kwargs:
            raise KeyError("Cannot init parameter without type")
        self.type = locate(kwargs['type'])
        self.stype = kwargs['type'] # type as string
        if self.type not in [int, str, float]:
            raise AttributeError("Type must be: str, int or float")

        if 'value' not in kwargs:
            raise KeyError("Cannot init parameter without value")
        try:
            self.value = self.type(kwargs['value'])
        except Exception as e:
            raise AttributeError("Value must have type {}".format(self.stype)) from e

        self.dir = None
        if 'dir' in kwargs:
            if self.stype == 'str':
                print("Ignoring direction for string type params")
            else:
                try:
                    self.dir = int(kwargs['dir'])
                except Exception as e:
                    raise AttributeError("Direction must be int")
                if self.dir not in [1, -1]:
                    raise AttributeError("Direction must be 1 or -1".format(self.stype))

        self.step = None
        if 'step' in kwargs:
            if self.stype == 'str':
                print("Ignoring step for string type params")
            else:
                try:
                    self.step = self.type(kwargs['step'])
                except Exception as e:
                    raise AttributeError("Step must have same type as value: {}".format(self.stype))

    def step_forward(self):
        """ This method adds one step to the value
            It is direction relative!
        """
        if self.stype == 'str':
            print("Not available for string params")
            return
        self.value = self.value + (self.dir * self.step)

    def step_backward(self):
        """ This method substracts one step from the value
            It is direction relative!
        """
        if self.stype == 'str':
            print("Not available for string params")
            return
        self.value = self.value - (self.dir * self.step)

    def change_dir(self):
        if self.stype == 'str':
            print("Not available for string params")
            return
        self.dir = -1 * self.dir

    def equality_format1(self):
        """This method returns -name=value"""
        return "-{}={}".format(self.name, self.value)

    def equality_format2(self):
        """This method returns --name=value"""
        return "--{}={}".format(self.name, self.value)

    def simple_format(self):
        """This method returns the value"""
        return " {}".format(self.value)

    def __str__(self):
        return "[name: {}, type: {}, value: {}, direction: {}, step: {}]".format(
                 self.name, self.stype, self.value, self.dir, self.step)
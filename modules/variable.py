import tkinter

class LogVar(tkinter.Variable):

    def __init__(self, root: tkinter.Tk, value: str = None, name: str = None) -> None:
        super().__init__(root, value, name)

    def get(self) -> list:
        """
            Return values as a list.
        """

        return list(self._tk.globalgetvar(self._name))

    def update(self, value: str) -> None:
        """
            Adds the given element to the beginning of the list.
        """

        data = self.get()
        data.insert(0, value)

        self._tk.globalsetvar(self._name, data)

class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()
 
    def __call__(self,num): return self.impl(num)
 
 
class _GetchUnix:
    def __init__(self):
        import tty, sys
 
    def __call__(self,num):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(num)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
 
 
class _GetchWindows:
    def __init__(self):
        import msvcrt
 
    def __call__(self,num):
        import msvcrt
        return msvcrt.getch()
 

getch = _Getch()


if __name__ == "__main__":
    
    #a = getch()
    while  1:
        print([getch(3)])
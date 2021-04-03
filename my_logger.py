from colorama import Fore, init, Style  # Colorir o console

init(convert=True)

def print_info(texto):
    print(f'{Fore.GREEN}[{Fore.WHITE}INFO{Fore.GREEN}]{Fore.CYAN} {texto} {Style.RESET_ALL}')

def print_pass(texto):
    print(f'{Fore.GREEN}[{Fore.WHITE}PASSED{Fore.GREEN}]{Fore.CYAN} {texto} {Style.RESET_ALL}')

def print_key(key):
    print(f'{Fore.GREEN}[{Fore.WHITE}KEY{Fore.GREEN}]{Fore.CYAN} UUID:\n{Fore.LIGHTBLACK_EX} {key} {Style.RESET_ALL}')

def print_erro(texto):
    print(f'{Fore.GREEN}[{Fore.RED}ERRO{Fore.GREEN}]{Fore.CYAN} {texto} {Style.RESET_ALL}')

def print_fail(texto):
    print(f'{Fore.GREEN}[{Fore.RED}FAIL{Fore.GREEN}]{Fore.CYAN} {texto} {Style.RESET_ALL}')

def print_time(texto):
    print(f'{Fore.GREEN}[{Fore.RED}TIME{Fore.GREEN}]{Fore.BLUE} {texto} {Style.RESET_ALL}')

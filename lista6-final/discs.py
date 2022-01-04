# coding=UTF-8
"""Module provides basic handling of vectors, discs and collision detection
"""

from random     import uniform                              #funkcja do generowania losowych liczb z predziału
from itertools  import combinations, islice, cycle          #kombinacje, zwracanie tablic wartości z generatorów i zapętlony iterator
from time       import time                                 #pomiar czasu
from matplotlib import pyplot       as plt                  #graficzna reprezentacja
from os         import environ                              #modyfikowanie zmiennych środowiskowych (tłumienie logów QT)
from warnings   import warn                                 #ostrzeżenia

#przykładowa paleta kolorów
STD_PALETTE =  ('#DC3522',
                '#e45d4e',
                '#374140',
                '#5b6b6a',
                '#22c9dc',
                '#0067A6',
                '#900B0A',
                '#d3100f',
                '#4C1B1B',
                '#883030',
                '#012840',
                '#025f98',
                '#002253',
                '#0045a8',
                '#0D47A1',
                '#030e20',
                '#010710')

#wiadomość ostrzeżenia o dużej ilości iteracji
WARNING_MSG = "\n\033[93mToo much iterations could be result of too many, or too large discs on too small area. \nConsider stopping program (CTRL+C) and modifing input data.\033[0m"

def suppress_qt_debug():                                    #wyłączenie wyświetlania zbędnych informacji z biblioteki QT pochodzącej z matplotlib
    """suppresss useless QT informations.

    Keyword arguments:
        -- nothing
    Returns:
        -- nothing (None type)
    """
    environ["QT_LOGGING_RULES"] = "*.debug=false"           #wyłącza wyświetlanie informacji debuggera QT (np. "qt5ct: using qt5ct plugin")
    try:
        del environ["SESSION_MANAGER"]                      #zapobiega wyświetlaniu się informacji o błędach session managera (np. typowy dla matplotlib "Qt: Session management error: Could not open network socket")
    except KeyError:                                        #jeżeli już zmodyfikowano
        pass                                                #nie rób nic

def make_vec(x,y):                                                              #utworzenie wektora
    """Form a vector.

    Keyword arguments:
    x, y    -- real numbers, coordinates in cartesian form
    Returns:
    [x, y]  -- list of coordinates
    """
    return [x,y]

def add_vec(vec1,vec2,c=1):                                                     #suma dwóch wektorów
    """Add two vectors.

    Keyword arguments:
    vec1, vec2  -- vectors defined as in make_vec function
    c           -- value to multiply second vector by (positive 1 by default)
    Returns:
                -- vector defined as in make_vec function
    """
    return [vec1[0]+c*vec2[0],vec1[1]+c*vec2[1]]

def make_disc(x,y,r):                                                           #utworzenie dysku ze współrzędnych i promienia
    """Form disc from coordinates and radius.

    Keyword arguments:
    x, y        -- real numbers, coordinates in cartesian form
    r           -- real number, value of disc radius
    Returns:
    ([x, y], r) -- tuple of vector, and radius
    """
    return ([x,y],r)

def make_disc_vec(vec,r):                                                       #utworzenie dysku z wektora i promienia
    """Form disc from vector and radius.

    Keyword arguments:
    vec         -- vector defined as in make_vec function
    r           -- real number, value of disc radius
    Returns:
    (vec, r)    -- tuple of vector, and radius
    """
    return (vec, r)
                                                                                
def move_disc(disc, vec, c=1):                                                  #przesunięcie dysku
    """Move disc by given vector.

    Keyword arguments:
    disc    -- disc defined as in make_disc, or make_disc_vec functions
    vec     -- vector defined as in make_vec function
    c       -- value to multiply vector by (positive 1 by default)
    Returns:
            -- nothing (None type)
    """
    disc[0][0] += c*vec[0]
    disc[0][1] += c*vec[1]

def vec_len(vec):                                                               #długość wektora
    """Return length of given vector.

    Keyword arguments:
    vec     -- vectors defined as in make_vec function
    Returns:
            -- numeric value of length
    """
    return (vec[0]**2+vec[1]**2)**.5

def len_from_disc(disc):                                                        #długość wektora od początku układu współrzędnych do środka dysku
    """Return length of vector from origin, to center of disc.

    Keyword arguments:
    disc    -- disc defined as in make_disc, or make_disc_vec functions
    Returns:
            -- numeric value of length
    """
    return (disc[0][0]**2+disc[0][1]**2)**.5

def gen_discs(n=100,area=((-15,15),(-15,15)),r_lims=(.5,.5)):                   #generowanie n dysków na zadanym obszarze, o zadanym przedziale promieniu
    """Generate random discs on given area.

    Keyword arguments:
    n       -- number of discs to generate
    area    -- iterable container of two iterable containers of numeric values of lower, and upper bonds, of two different axes (ex. form: [[x_0, x_m],[y_0, y_m]])
    r_lims  -- iterable container of numeric values of lower, and upper bonds of radius
    Returns:
    dlist   -- list of discs
    """
    dlist = [None]*n                                                                            #inicjalizacja listy
    for i in range(n):
        r           = uniform(r_lims[0],r_lims[1])                                              #generowania losowego promienia
        posx, posy  = uniform(area[0][0]+r,area[0][1]-r), uniform(area[1][0]+r, area[1][1]-r)   #generowanie losowej pozycji na danym obszarze
        dlist[i]    = make_disc(posx,posy,r)                                                    #dodanie nowego dysku do listy

    return dlist                                                                                #zwrócenie listy

def uncollide(dlist,n1,n2):                             #usunięcie kolizji dwóch dysków z listy
    """Uncollide two discs from list of discs.

    Keyword arguments:
    dlist   -- list of discs
    n1, n2  -- indexes of discs in list of discs
    Returns:
            -- boolean which determines if discs were modified or not
    """
    between = add_vec(dlist[n2][0],dlist[n1][0],-1)     #utworzenie wektora symbolizującego odcinek pomiędzy środkami dwóch okręgów
    r_sum = dlist[n1][1]+dlist[n2][1]                   #suma promieni obydwu okręgów
    l = vec_len(between)                                #długość wektora zdefiniowanego wyżej
    if r_sum > l:                                       #jeżeli dyski na siebie nachodzą
        mid = [x/2 for x in between]                    #środek tego wektora
        l = vec_len(between)                            #długość wektora zdefiniowanego wyżej
        x = r_sum-l                                     #określenie długości odcinka znajdującego się na prostej łączącej środki okręgów, 
    #                                                    zdefiniowanego na ich części wspólnej
        x *= uniform(1.001,2)                           #fragment uniemożliwiający powstanie potencjalnie nieskończonej pętli
    #                                                    wprowadzenie do przesunięcia losowego błędu zawyżenia odległości od 0.1% do 100%
    #                                                    graficzna reprezentacja: https://www.geogebra.org/m/ztyav7qw
        l_mid = l/2                                     #połowa długości wektora zdefiniowanego wyżej

        move_disc(dlist[n1], mid, -(x/(2*l_mid)))       #przemieszczanie dysków od środka pomiędzy nimi, wzdłuż prostej opartej na wektorze pomiędzy ich środkami
        move_disc(dlist[n2], mid, (x/(2*l_mid)))
        return True                                     #zwróć prawda jeżeli zmiana
    else:                                               
        return False                                    #zwróć fałsz jeśli nie było kolizji

def push2area(dlist,n,area):                            #umiejscowienie dysków wychodzących poza dany obszar, w tym obszarze
    """Push exceeding disc from list to given area

    Keyword arguments:
    dlist   -- list of discs
    n       -- index of disc in list
    area    -- iterable container of two iterable containers of numeric values of lower, and upper bonds, of two different axes (ex. form: [[x_0, x_m],[y_0, y_m]])
    Returns:
    flag    -- boolean which determines if disc were modified or not
    """
    flag = False                                                #flaga określająca czy zostały wprowadzone jakieś zmiany
    #sprawdzenie czy okrąg znajduje się w obrębie danego obszaru
    if dlist[n][0][0] - dlist[n][1] < area[0][0]:
        dlist[n][0][0] = area[0][0] + dlist[n][1]*uniform(1,2)
        flag = True
    elif dlist[n][0][0] + dlist[n][1] > area[0][1]:
        dlist[n][0][0] = area[0][1] - dlist[n][1]*uniform(1,2)
        flag = True
    if dlist[n][0][1] - dlist[n][1] < area[1][0]:
        dlist[n][0][1] = area[1][0] + dlist[n][1]*uniform(1,2)
        flag = True
    elif dlist[n][0][1] + dlist[n][1] > area[1][1]:
        dlist[n][0][1] = area[1][1] - dlist[n][1]*uniform(1,2)
        flag = True
    return flag                                                  #zwrócenie flagi

def process_list(dlist,area):                       #przetworzenie listy dysków pod kątem usunięcia kolizji i utrzymania dysków na zadanym obszarze
    """Perform removal of collisions of discs on list inside given area.

    Keyword arguments:
    dlist   -- list of discs
    area    -- iterable container of two iterable containers of numeric values of lower, and upper bonds, of two different axes (ex. form: [[x_0, x_m],[y_0, y_m]])
    Returns:
            -- nothing (None type)
    """
    n = len(dlist)                                  #ilość elementów listy
    combs = tuple(combinations(range(n),2))         #przechowania kombinacji dwuelementowych indeksów listy
    rng = tuple(range(n))                           #przechowanie listy indeksów
    flag = True                                     #flaga zmian listy
    m = 0
    print('Removing collisions of',n,'elements...') #info
    print('Checking {} pairs of discs per iteration.'.format(int((n-1)*n*.5)))
    begin = time()                                  #początek pomiaru czasu
    while flag:                                     #pętla działająca dopóki wprowadzane są zmiany
        #print('...')
        flag = False                                #wstępna wartość flagi dla rozpocząecia pętli - fałsz
        m += 1
        for i in combs:                             #usuwanie kolizji dla par wszystkich dysków z listy
            if uncollide(dlist,i[0],i[1]):  flag = True
        for i in rng:                               #upewnienie się czy wszystkie dyski pozostały na danym obszarze
            if push2area(dlist,i,area):     flag = True
        if m > 120:                                 #ostrzeżenie o dużej ilości iteracji
            warn(\
                WARNING_MSG,category=RuntimeWarning)
    end = time()                                    #koniec pomiaru czasu
    print('Done in {:.3f} sec. and {} iterations.'.format(end-begin,m))    #info

def dlist2plot(dlist,ax, palette=None):                 #dodanie listy dysków do obiektu typu axes biblioteki matplotlib
    """Add list of discs to plot.

    Keyword arguments:
    dlist   -- list of discs
    ax      -- pyplot axes object
    palette -- iterable container of pyplot compatible color definitions
    Returns:
            -- nothing (None type)
    """
    n = len(dlist)                                      #ilość elementów na liście
    p = None                                            #przygotowanie zmiennej określającej czy została wprowadzona paleta kolorów
    if palette == None:                                 #jeżeli nie wprowadzono palety
        clr = '#5B9279'                                 #dyski będą wyświetlane w takim kolorze
        p = False                                       #zmienna ustawiona na fałsz
    else:                                               #jeżeli wrpowadzono paletę
        clr = [x for x in islice(cycle(palette),n)]     #utwórz listę kolorów dla każdego elementu listy (kolory stałe dla pozycji dysku na liście)
        p = True                                        #zmienna ustawiona na prawdę

    for i,disc in enumerate(dlist):                     #dla wszystkich dysków na liście
        ax.add_patch(plt.Circle((disc[0][0],disc[0][1]),disc[1],alpha=.4,color=(clr[i] if p else clr))) #dodaj do wyświetlenia okrąg o zadanych parametrach

def area2plot(area, ax, clr='#600201'):
    """Add area limits to plot.

    Keyword arguments:
    area    -- iterable container of two iterable containers of numeric values of lower, and upper bonds, of two different axes (ex. form: [[x_0, x_m],[y_0, y_m]])
    ax      -- pyplot axes object
    clr     -- pyplot compatible color definition
    Returns:
            -- nothing (None type)
    """
    ax.add_patch(plt.Rectangle((area[0][0],area[1][0]),area[0][1]-area[0][0],area[1][1]-area[1][0], color=clr, fill=False, linestyle='--'))

def plot_uncolliding(dlist,area, palette=None): #pokaż na wykresie proces usunięcia kolizji dysków z listy
    """Process and display on plot list of discs.

    Keyword arguments:
    dlist   -- list of discs
    area    -- iterable container of two iterable containers of numeric values of lower, and upper bonds, of two different axes (ex. form: [[x_0, x_m],[y_0, y_m]])
    palette -- iterable container of pyplot compatible color definitions
    Returns:
            -- nothing (None type)
    """                                      
    suppress_qt_debug()                         #wyłączenie informacji debuggera QT
    plt.close('all')                            #zamknięcie aktywnych okien pyplot
    fig,ax = plt.subplots(nrows=1,ncols=2)      #utworzenie dwóch mniejszych wykresów
    dlist2plot(dlist,ax[0],palette)             #dodanie dysków z listy do wykresu
    area2plot(area,ax[0])                       #dodanie obszaru do wykresu
    process_list(dlist,area)                    #usunięcie kolizji na obszarze
    dlist2plot(dlist,ax[1],palette)             #dodanie dysków po zmianie do wykresu
    area2plot(area,ax[1])                       #dodanie obszaru do wykresu
    [(ax[i].autoscale_view(), ax[i].set_aspect('equal')) for i in range(2)] #dopasowanie skali i stosunku osi dla powyższych wykresów
    ax[0].set_title("Before shift")             #dodanie tytułów
    ax[1].set_title("After shift")
    plt.show()                                  #wyświetlenie wykresów    
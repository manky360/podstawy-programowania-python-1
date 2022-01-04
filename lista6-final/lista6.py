from discs import gen_discs, plot_uncolliding, STD_PALETTE

def main():
    n       = 625                               #ilość dysków do wygenerowania
    area    = [[-15,15],[-15,15]]               #przestrzeń na której dyski mają być umieszczone
    r_lims  = [.3,.7]                           #granice w jakich mają mieścić się długości promieni dysków
    dlist   = gen_discs(n, area, r_lims)        #wygenerowanie dysków
    plot_uncolliding(dlist,area,STD_PALETTE)    #graficzna reprezentacja usunięcia kolizji z listy dysków

main()
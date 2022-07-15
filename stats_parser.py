import pstats
p = pstats.Stats('perfoutput.txt')
p.sort_stats('cumulative').print_stats(20)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def draw_free(xs, reses, output):
    plt.xticks(xs)
    if len(reses) == 0 or len(reses[0]) == 0:
        print('empty result')
        return
    for key in reses[0][0]:
        for res in reses:
            ys = [y[key] for y in res]
            plt.plot(xs, ys, "-D")
        plt.savefig(''.join([output.split('.')[0], '-', key , '.pdf']))
        plt.close()